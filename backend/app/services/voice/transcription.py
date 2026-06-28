"""
Multilingual voice transcription using OpenAI Whisper
Supports: English, Hindi, Telugu, Tamil, Malayalam, Kannada
"""
import whisper
import tempfile, os

SUPPORTED_LANGUAGES = ["en", "hi", "te", "ta", "ml", "kn"]

class VoiceTranscriptionService:
    def __init__(self, model_size: str = "medium"):
        self.model = whisper.load_model(model_size)

    async def transcribe(self, audio_bytes: bytes, language: str = None) -> dict:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name

        try:
            result = self.model.transcribe(
                tmp_path,
                language=language if language in SUPPORTED_LANGUAGES else None,
                task="transcribe",
            )
            return {
                "text":     result["text"],
                "language": result["language"],
                "segments": result["segments"],
            }
        finally:
            os.unlink(tmp_path)
