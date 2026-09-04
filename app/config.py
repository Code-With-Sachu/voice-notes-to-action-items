"""
Configuration and constants for the Voice Notes -> Action Items app.
"""

import os

# Load .env file if python-dotenv is available (local dev convenience).
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# API configuration
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Models
TRANSCRIPTION_MODEL = "whisper-1"          # OpenAI Whisper API model
SUMMARY_MODEL = "gpt-4o-mini"              # Fast + cheap, good enough for summaries

# ---------------------------------------------------------------------------
# App settings
# ---------------------------------------------------------------------------
APP_TITLE = "🎙️ Voice Notes → Action Items"
APP_DESCRIPTION = (
    "Upload or record a voice memo and get a clean summary with clear, "
    "actionable next steps — no more re-listening to rambling audio notes."
)

# Whisper API hard limit is 25 MB per file.
MAX_FILE_SIZE_MB = 25

# Supported audio formats (matches what OpenAI Whisper API accepts)
SUPPORTED_FORMATS = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]


def keys_configured() -> bool:
    """Returns True if the OpenAI API key is set."""
    return bool(OPENAI_API_KEY)
