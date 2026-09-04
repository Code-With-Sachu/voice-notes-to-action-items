"""
Voice Notes -> Action Items
A Streamlit app that transcribes a voice memo and turns it into a clean
summary with clear action items.

Run with:  streamlit run main.py
"""

import streamlit as st

from app.config import APP_TITLE, APP_DESCRIPTION, MAX_FILE_SIZE_MB, SUPPORTED_FORMATS, keys_configured
from app.transcription import transcribe_audio, TranscriptionError
from app.summarizer import summarize_transcript, SummarizationError, NoteResult

st.set_page_config(page_title="Voice Notes → Action Items", page_icon="🎙️", layout="centered")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "note_result" not in st.session_state:
    st.session_state.note_result = None  # NoteResult | None
if "processed_filename" not in st.session_state:
    st.session_state.processed_filename = None


def process_audio(file_bytes: bytes, filename: str) -> NoteResult:
    with st.spinner("Transcribing audio..."):
        transcript = transcribe_audio(file_bytes, filename)
    with st.spinner("Summarizing and extracting action items..."):
        note = summarize_transcript(transcript)
    return note


def render_note(note: NoteResult):
    st.subheader(note.title)

    st.markdown("**Summary**")
    st.write(note.summary or "_No summary generated._")

    st.markdown("**Action Items**")
    if note.action_items:
        for item in note.action_items:
            st.checkbox(item, key=f"action_{hash(item)}")
    else:
        st.caption("No action items identified in this note.")

    if note.key_topics:
        st.markdown("**Topics**")
        st.write(" ".join(f"`{t}`" for t in note.key_topics))

    with st.expander("Full transcript"):
        st.write(note.raw_transcript)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.title(APP_TITLE)
st.write(APP_DESCRIPTION)

if not keys_configured():
    st.error(
        "⚠️ OpenAI API key not found. Set the `OPENAI_API_KEY` environment variable "
        "(or add it to a `.env` file) before using this app."
    )
    st.stop()

st.divider()

tab_upload, tab_record = st.tabs(["📁 Upload audio", "🎤 Record audio"])

uploaded_bytes = None
uploaded_filename = None

with tab_upload:
    uploaded_file = st.file_uploader(
        "Upload a voice memo",
        type=SUPPORTED_FORMATS,
        help=f"Max file size: {MAX_FILE_SIZE_MB} MB. Supported formats: {', '.join(SUPPORTED_FORMATS)}",
    )
    if uploaded_file is not None:
        size_mb = uploaded_file.size / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            st.error(f"File is {size_mb:.1f} MB, which exceeds the {MAX_FILE_SIZE_MB} MB limit.")
        else:
            uploaded_bytes = uploaded_file.read()
            uploaded_filename = uploaded_file.name
            st.audio(uploaded_bytes)

with tab_record:
    recorded_audio = st.audio_input("Record a voice memo")
    if recorded_audio is not None:
        uploaded_bytes = recorded_audio.read()
        uploaded_filename = "recording.wav"
        st.audio(uploaded_bytes)

st.divider()

process_clicked = st.button(
    "✨ Process Voice Note",
    type="primary",
    disabled=uploaded_bytes is None,
    use_container_width=True,
)

if process_clicked and uploaded_bytes is not None:
    try:
        note = process_audio(uploaded_bytes, uploaded_filename)
        st.session_state.note_result = note
        st.session_state.processed_filename = uploaded_filename
    except TranscriptionError as e:
        st.error(f"Transcription error: {e}")
    except SummarizationError as e:
        st.error(f"Summarization error: {e}")
    except Exception as e:  # noqa: BLE001 - surface unexpected errors to the user
        st.error(f"Unexpected error: {e}")

if st.session_state.note_result is not None:
    st.divider()
    st.markdown("### 📋 Result")
    render_note(st.session_state.note_result)

    if st.button("🗑️ Clear result"):
        st.session_state.note_result = None
        st.session_state.processed_filename = None
        st.rerun()

st.divider()
st.caption(
    "Built with Streamlit, OpenAI Whisper API (transcription), and OpenAI GPT (summarization)."
)
