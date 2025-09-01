import webrtcvad

# Simple frame-based VAD gate; expects 20ms 16kHz PCM16 frames
class FrameVAD:
    def __init__(self, aggressiveness: int = 2):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.frame_ms = 20
        self.expected_bytes = int(16000 * 2 * self.frame_ms / 1000)

    def accept_frame(self, frame: bytes) -> bool:
        if len(frame) != self.expected_bytes:
            return True  # pass-through if unexpected size
        return self.vad.is_speech(frame, 16000)