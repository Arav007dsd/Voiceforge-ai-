# VoiceForge AI

A responsive text-to-speech studio powered by the real Microsoft Edge TTS voice catalogue and FastAPI.

## Stack
- React + Vite + Tailwind CSS
- FastAPI + edge-tts (async)
- MP3 output; no API key required for Edge TTS

## Local development

### Backend
Python 3.10+ recommended.

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Set `VITE_API_BASE_URL=http://localhost:8000` in frontend/.env. Open the Vite URL.

## Deployment

### Backend on Render
1. Create a new Web Service from this repository.
2. Set Root Directory to `backend`.
3. Runtime: Python; Build: `pip install -r requirements.txt`.
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. Set `FRONTEND_ORIGINS` to your Vercel production URL (comma-separated for multiple origins).

A `render.yaml` blueprint is included. The API exposes `/api/health`, `/api/voices`, and `/api/tts`.

### Frontend on Vercel
1. Import this repository in Vercel.
2. Set Root Directory to `frontend`.
3. Framework preset: Vite.
4. Set `VITE_API_BASE_URL` to the deployed Render service origin, without a trailing slash.
5. Deploy.

## API
- `GET /api/health` — service status
- `GET /api/voices` — dynamically fetches Microsoft Edge TTS voices
- `POST /api/tts` — JSON body: `{text, voice, rate, pitch, volume}`; returns MP3 bytes

## Notes
- Edge TTS is an online service; generation requires internet access and may be subject to Microsoft's service limits or availability.
- Voice availability and gender metadata come from the live Edge TTS catalogue. Voice preview uses the same generation endpoint.
- History is stored locally in the visitor's browser. Generated MP3s are returned directly and are not permanently stored on the server.
- Do not submit confidential or sensitive text. This project is an independent interface and is not affiliated with Microsoft or ElevenLabs.
- FFmpeg is not required for the current MP3-only pipeline; it can be added later for post-processing or format conversion.
