# VoiceForge AI

A modern text-to-speech studio using React, FastAPI, and the live Microsoft Edge TTS voice catalogue.

## Deploy the entire app on Vercel

The repository is configured as a **single Vercel project** with two Vercel Services:
- Frontend: Vite + React, served by Vercel.
- Backend: FastAPI + edge-tts, served by Vercel Python Functions.

### One-time setup
1. Import this GitHub repository into Vercel: https://vercel.com/new
2. Select `Arav007dsd/Voiceforge-ai-`.
3. Set the **Root Directory** to the repository root (leave it as `./`).
4. Do not set a separate frontend or backend root in the Vercel project settings. The root `vercel.json` configures both services.
5. Deploy.

The frontend calls `/api/health`, `/api/voices`, and `/api/tts` on the same Vercel domain. No backend URL or CORS environment variable is required for production.

> Vercel Services support depends on availability for the account/team. The deployment configuration uses the Vercel multi-service routing format.

## Local development

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
# Set VITE_API_BASE_URL=http://localhost:8000 in .env
npm run dev
```

## API
- `GET /api/health` — service health
- `GET /api/voices` — dynamically retrieves the current Edge TTS voice catalogue
- `POST /api/tts` — JSON body: `{ "text": "...", "voice": "en-US-AriaNeural", "rate": "+0%", "pitch": "+0Hz", "volume": "+0%" }`; returns MP3 bytes.

## Notes
- Edge TTS is an online service. Voice availability and generation depend on Microsoft's service availability and may be subject to service limits.
- Audio is generated into a secure temporary file and removed after the response.
- Browser history is stored locally in the visitor's browser; generated MP3s are not permanently stored on the server.
- Do not submit confidential or sensitive text.
- VoiceForge AI is independent and is not affiliated with Microsoft or ElevenLabs.
- FFmpeg is not needed for direct MP3 generation; it can be added for future audio post-processing.

## Desktop and mobile installers

The `.github/workflows/build-apps.yml` workflow builds:
- Windows x64 installer: `VoiceForge-Setup.exe`
- Android debug installer: `VoiceForge-Android.apk`

On each push to `main`, GitHub Actions builds both packages and uploads them to the GitHub Release tagged `latest`. The website's **Get the App** buttons point directly to these release assets. The Android APK is an unsigned/debug build intended for testing; a signed release build is required for public distribution. iPhone and iPad use the installable PWA rather than an IPA.
