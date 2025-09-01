import os
import io
import queue
from typing import Optional, Tuple

import numpy as np
import soundfile as sf
from google.cloud import speech

SAMPLE_RATE = 16000

class GoogleASR:
    """Streaming ASR wrapper around Google Cloud Speech-to-Text.
    Simple chunk-based with optional endpointer handled by client or VAD.
    """
    def __init__(self):
        self.client = speech.SpeechClient()
        self._requests_q: "queue.Queue[bytes]" = queue.Queue()
        self._closed = True

    def start_streaming(self):
        self._closed = False
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code=os.getenv("ASR_LANGUAGE_EN", "en-US"),
            enable_automatic_punctuation=True,
            model="default",
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
            single_utterance=False,
        )
        def reqs():
            while not self._closed:
                chunk = self._requests_q.get()
                if chunk is None:
                    break
                yield speech.StreamingRecognizeRequest(audio_content=chunk)
        self._call = self.client.streaming_recognize(streaming_config, reqs())
        return True

    def process_chunk(self, pcm16: bytes) -> Tuple[Optional[str], bool]:
        # Enqueue audio for GCP and pull available responses non-blocking
        self._requests_q.put(pcm16)
        text = None
        is_final = False
        try:
            resp = next(self._call, None)
            if resp and resp.results:
                result = resp.results[0]
                if result.alternatives:
                    text = result.alternatives[0].transcript
                    is_final = result.is_final
        except StopIteration:
            pass
        return text, is_final

    def finish_streaming(self) -> Optional[str]:
        self._requests_q.put(None)
        final_text = None
        try:
            for resp in self._call:
                if resp.results and resp.results[0].is_final:
                    final_text = resp.results[0].alternatives[0].transcript
        except Exception:
            pass
        return final_text

    def close_stream(self):
        self._closed = True
        try:
            self._requests_q.put(None)
        except Exception:
            pass