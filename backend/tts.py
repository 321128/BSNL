import io
import numpy as np
import soundfile as sf
from TTS.api import TTS

class CoquiTTS:
    def __init__(self):
        # Note: you must set a Garo-capable model if available. Placeholder uses default multi-lingual if supported
        model_name = "tts_models/multilingual/multi-dataset/your_garo_model"  # TODO: replace with actual
        try:
            self.tts = TTS(model_name)
        except Exception as e:
            self.tts = None
            print(f"TTS init failed: {e}")

    def synthesize(self, text: str, language: str) -> bytes:
        if not self.tts:
            raise RuntimeError("TTS model not initialized. Set a valid model_name for Garo.")
        # Generate mono 22k or 16k audio depending on model; resampling is handled by TTS
        wav = self.tts.tts(text)
        wav = np.asarray(wav, dtype=np.float32)
        # Convert to 16-bit WAV bytes
        buf = io.BytesIO()
        sf.write(buf, wav, 22050, format='WAV', subtype='PCM_16')
        return buf.getvalue()