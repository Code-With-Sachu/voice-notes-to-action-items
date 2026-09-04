"""
Configuration and constants for the Voice Notes -> Action Items app.
"""

import os

# Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ---------------------------------------------------------------------------
# API configuration
# ---------------------------------------------------------------------------

# First try environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# If running on Streamlit Cloud, try Streamlit Secrets
if not OPENAI_API_KEY:
    try:
        import streamlit as st
        OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        pass


# Models
TRANSCRIPTION_MODEL = "whisper-1"
SUMMARY_MODEL = "gpt-4o-mini"


# ---------------------------------------------------------------------------
# App settings
# ---------------------------------------------------------------------------

APP_TITLE = "🎙️ Voice Notes → Action Items"

APP_DESCRIPTION = (
    "Upload or record a voice memo and get a clean summary with clear, "
    "actionable next steps — no more re-listening to rambling audio notes."
)

MAX_FILE_SIZE_MB = 25

SUPPORTED_FORMATS = [
    "mp3",
    "mp4",
    "mpeg",
    "mpga",
    "m4a",
    "wav",
    "webm",
]


def keys_configured() -> bool:
    """Returns True if the OpenAI API key is configured."""
    return bool(OPENAI_API_KEY)
