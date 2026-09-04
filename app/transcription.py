"""
Speech-to-text transcription using the OpenAI Whisper API.
"""

import io
from openai import OpenAI, OpenAIError

from app.config import OPENAI_API_KEY, TRANSCRIPTION_MODEL


class TranscriptionError(Exception):
    """Raised when audio transcription fails."""
    pass


def transcribe_audio(file_bytes: bytes, filename: str) -> str:
    """
    Sends audio bytes to the OpenAI Whisper API and returns the transcript text.

    Args:
        file_bytes: Raw bytes of the audio file.
        filename: Original filename (used so the API can infer the format).

    Returns:
        The transcribed text.

    Raises:
        TranscriptionError: If the API key is missing or the API call fails.
    """
    if not OPENAI_API_KEY:
        raise TranscriptionError(
            "OpenAI API key is not configured. Set OPENAI_API_KEY in your environment "
            "or .env file."
        )

    client = OpenAI(api_key=OPENAI_API_KEY)

    # The Whisper API needs a file-like object with a name attribute so it
    # can infer the audio format from the extension.
    audio_file = io.BytesIO(file_bytes)
    audio_file.name = filename

    try:
        response = client.audio.transcriptions.create(
            model=TRANSCRIPTION_MODEL,
            file=audio_file,
        )
    except OpenAIError as e:
        raise TranscriptionError(f"Transcription failed: {e}") from e

    transcript = getattr(response, "text", "").strip()
    if not transcript:
        raise TranscriptionError("Transcription returned empty text. Try a clearer recording.")

    return transcript
