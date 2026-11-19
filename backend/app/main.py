from __future__ import annotations

import asyncio
import re
import tempfile
from pathlib import Path
from typing import Literal

import edge_tts
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from starlette.background import BackgroundTask

app = FastAPI(title="VoiceForge AI API", version="1.0.0")

origins = [item.strip() for item in __import__("os").getenv(
    "FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

MAX_CHARS = 100000
RATE_RE = re.compile(r"^[+-]?\d{1,3}%$")
PITCH_RE = re.compile(r"^[+-]?\d{1,3}Hz$")
VOLUME_RE = re.compile(r"^[+-]?\d{1,3}%$")


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_CHARS)
    voice: str = Field(min_length=3, max_length=100)
    rate: str = Field(default="+0%", pattern=r"^[+-]?\d{1,3}%$")
    pitch: str = Field(default="+0Hz", pattern=r"^[+-]?\d{1,3}Hz$")
    volume: str = Field(default="+0%", pattern=r"^[+-]?\d{1,3}%$")

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Please enter some text.")
        return value.strip()


_voice_cache: list[dict] = []
_voice_cache_at = 0.0
_voice_lock = asyncio.Lock()


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "VoiceForge AI", "engine": "edge-tts"}


@app.get("/api/voices")
async def voices():
    global _voice_cache, _voice_cache_at
    import time
    async with _voice_lock:
        if _voice_cache and time.time() - _voice_cache_at < 900:
            return {"voices": _voice_cache, "cached": True}
        try:
            raw = await edge_tts.list_voices()
            _voice_cache = [
                {
                    "name": item.get("ShortName"),
                    "display_name": item.get("FriendlyName") or item.get("ShortName"),
                    "locale": item.get("Locale"),
                    "gender": item.get("Gender", "Unknown"),
                }
                for item in raw if item.get("ShortName")
            ]
            _voice_cache_at = time.time()
            return {"voices": _voice_cache, "cached": False}
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Could not retrieve live voices: {exc}") from exc


def split_text(text: str, limit: int = 2500) -> list[str]:
    # Split at sentence/word boundaries so long scripts are sent in manageable
    # Edge TTS requests while preserving the original text order.
    import re
    sentences = re.split(r'(?<=[.!?。！？])\\s+', text.strip())
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        while len(sentence) > limit:
            cut = sentence.rfind(" ", 0, limit + 1)
            if cut < 1:
                cut = limit
            piece, sentence = sentence[:cut].strip(), sentence[cut:].strip()
            if current:
                chunks.append(current)
                current = ""
            if piece:
                chunks.append(piece)
        if not sentence:
            continue
        candidate = (current + " " + sentence).strip()
        if len(candidate) > limit and current:
            chunks.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


@app.post("/api/tts")
async def text_to_speech(payload: SpeechRequest):
    try:
        available = await edge_tts.list_voices()
        if not any(item.get("ShortName") == payload.voice for item in available):
            raise HTTPException(status_code=400, detail="Selected voice is not in the current Edge TTS catalogue.")

        temp = tempfile.NamedTemporaryFile(prefix="voiceforge_", suffix=".mp3", delete=False)
        temp_path = Path(temp.name)
        temp.close()
        try:
            # Edge TTS is called in smaller chunks. MP3 frame streams are
            # appended in order into one downloadable MP3 file.
            with temp_path.open("wb") as output:
                for part in split_text(payload.text):
                    communicate = edge_tts.Communicate(
                        part, payload.voice,
                        rate=payload.rate, pitch=payload.pitch, volume=payload.volume,
                    )
                    async for item in communicate.stream():
                        if item.get("type") == "audio":
                            output.write(item.get("data", b""))
            if not temp_path.exists() or temp_path.stat().st_size == 0:
                raise RuntimeError("The speech engine returned an empty audio file.")
            return FileResponse(
                path=temp_path,
                media_type="audio/mpeg",
                filename="voiceforge-audio.mp3",
                background=BackgroundTask(lambda: temp_path.unlink(missing_ok=True)),
                headers={"Cache-Control": "no-store"},
            )
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Speech generation failed: {exc}") from exc
