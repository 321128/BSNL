# Garo↔English Voice Agent (ASR→Translate→UI and UI→Translate→TTS)

## Overview
- **Caller side**: Garo speech → ASR → Garo text → Translate → English text → Agent UI
- **Agent side**: Agent English speech → ASR → English text → Translate → Garo text → TTS → Garo speech

This repo provides a FastAPI backend for streaming ASR and TTS, plus a Vite React UI scaffold (to be added).

## Backend
- FastAPI endpoints:
  - `GET /health`
  - `POST /translate` { text, source_lang, target_lang }
  - `POST /tts` { text, language } → returns WAV bytes
  - `WS /ws/asr` accepts 16kHz PCM16 20ms frames; returns `{ text, final }`
- Engines:
  - **ASR**: Google Cloud Speech-to-Text
  - **Translate**: Google Cloud Translate
  - **TTS**: Coqui TTS (placeholder; requires Garo-capable model)
  - **VAD**: WebRTC VAD (20ms frames)

## Setup
1. Create Google Cloud project and enable Speech-to-Text and Translate APIs.
2. Place service account key at `backend/credentials/gcp-service-account.json` or mount via Docker.
3. Copy `.env.example` to `.env` and adjust values.
4. Install deps and run:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r backend/requirements.txt
   uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
   ```

## WebSocket audio format
- 16 kHz mono PCM16
- 20ms frames (640 samples → 1280 bytes)

## TODO
- Implement agent-ui (Vite React) with microphone streaming and teleprompter.
- Wire language routing (Garo↔English) in UI.
- Provide a real Garo TTS model or API.
- Docker compose for backend + UI.