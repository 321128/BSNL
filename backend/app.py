from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
from dotenv import load_dotenv
from pydantic import BaseModel

from backend.asr import GoogleASR
from backend.translate import GoogleTranslator
from backend.tts import CoquiTTS
from backend.vad import FrameVAD

load_dotenv()

app = FastAPI(title="Garo-English Agent Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

translator = GoogleTranslator()
asr = GoogleASR()
tts = CoquiTTS()
vad = FrameVAD()

class TranslateBody(BaseModel):
    text: str
    source_lang: str
    target_lang: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/translate")
async def translate_text(body: TranslateBody):
    try:
        out = translator.translate(body.text, body.source_lang, body.target_lang)
        return {"text": out}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.websocket("/ws/asr")
async def ws_asr(ws: WebSocket):
    await ws.accept()
    # Protocol: client sends binary PCM16 16kHz frames; we'll VAD and send partial/final texts
    try:
        stream = asr.start_streaming()
        async for message in ws.iter_bytes():
            if not isinstance(message, (bytes, bytearray)):
                continue
            # VAD gate
            speech = vad.accept_frame(message)
            if speech:
                text, is_final = asr.process_chunk(message)
                if text:
                    await ws.send_json({"text": text, "final": is_final})
        # client closed
        final_text = asr.finish_streaming()
        if final_text:
            await ws.send_json({"text": final_text, "final": True})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await ws.send_json({"error": str(e)})
    finally:
        asr.close_stream()
        await ws.close()

class TTSBody(BaseModel):
    text: str
    language: str

@app.post("/tts")
async def tts_synthesize(body: TTSBody):
    try:
        wav_bytes = tts.synthesize(body.text, body.language)
        return JSONResponse(content=wav_bytes, media_type="audio/wav")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})