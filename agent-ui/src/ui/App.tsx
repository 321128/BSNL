import React, { useEffect, useRef, useState } from 'react'

const SAMPLE_RATE = 16000
const FRAME_MS = 20
const BYTES_PER_SAMPLE = 2

function floatTo16BitPCM(input: Float32Array) {
  const output = new DataView(new ArrayBuffer(input.length * 2))
  let offset = 0
  for (let i = 0; i < input.length; i++, offset += 2) {
    let s = Math.max(-1, Math.min(1, input[i]))
    output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true)
  }
  return output.buffer
}

export default function App() {
  const [connected, setConnected] = useState(false)
  const [partial, setPartial] = useState('')
  const [finals, setFinals] = useState<string[]>([])
  const wsRef = useRef<WebSocket | null>(null)
  const mediaRef = useRef<MediaStream | null>(null)

  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRef.current = stream

    const audioCtx = new AudioContext({ sampleRate: SAMPLE_RATE })
    const source = audioCtx.createMediaStreamSource(stream)
    const processor = audioCtx.createScriptProcessor(1024, 1, 1)

    const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://localhost:1221/ws/asr`)
    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onmessage = (ev) => {
      const data = JSON.parse(ev.data)
      if (data.error) console.error(data.error)
      if (data.text) {
        if (data.final) setFinals(f => [...f, data.text])
        else setPartial(data.text)
      }
    }
    wsRef.current = ws

    let buffer: Float32Array[] = []
    let bufferSamples = 0
    const frameSamples = (SAMPLE_RATE * FRAME_MS) / 1000

    processor.onaudioprocess = (e) => {
      const chunk = e.inputBuffer.getChannelData(0)
      buffer.push(new Float32Array(chunk))
      bufferSamples += chunk.length

      while (bufferSamples >= frameSamples) {
        const frame = new Float32Array(frameSamples)
        let offset = 0
        while (offset < frameSamples && buffer.length) {
          const first = buffer[0]
          const needed = frameSamples - offset
          const take = Math.min(needed, first.length)
          frame.set(first.subarray(0, take), offset)
          offset += take
          if (take < first.length) buffer[0] = first.subarray(take)
          else buffer.shift()
        }
        bufferSamples -= frameSamples
        const pcm = floatTo16BitPCM(frame)
        ws.send(pcm)
      }
    }

    source.connect(processor)
    processor.connect(audioCtx.destination)
  }

  function stop() {
    wsRef.current?.close()
    mediaRef.current?.getTracks().forEach(t => t.stop())
    setConnected(false)
  }

  return (
    <div style={{ padding: 16, fontFamily: 'sans-serif' }}>
      <h2>Agent UI (English teleprompter)</h2>
      <div>
        {connected ? (
          <button onClick={stop}>Stop</button>
        ) : (
          <button onClick={start}>Start Mic</button>
        )}
      </div>

      <h3>Partial</h3>
      <div style={{ minHeight: 24 }}>{partial}</div>
      <h3>Final</h3>
      <div>
        {finals.map((f, i) => (
          <div key={i}>{f}</div>
        ))}
      </div>
    </div>
  )
}