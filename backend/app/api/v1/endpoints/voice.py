"""Voice intake — multilingual transcription (Whisper), loaded lazily/optionally."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.models.admin.doctor import Doctor
from app.core.config import settings
from app.api.dependencies.auth import get_current_doctor

router = APIRouter()
_service = None


def _get_service():
    global _service
    if _service is None:
        try:
            from app.services.voice.transcription import VoiceTranscriptionService
            _service = VoiceTranscriptionService(settings.WHISPER_MODEL)
        except Exception as exc:  # noqa: BLE001 — whisper/ffmpeg not installed
            raise HTTPException(status_code=503, detail=f"Voice transcription unavailable: {exc}")
    return _service


@router.post("/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    language: str = "",
    doctor: Doctor = Depends(get_current_doctor),
):
    service = _get_service()
    audio_bytes = await audio.read()
    return await service.transcribe(audio_bytes, language or None)
