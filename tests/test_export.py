"""
Unit tests for app/export.py.

Run with: python -m pytest tests/ -v
"""

from app.summarizer import NoteResult
from app.export import export_notes_to_pdf, export_note_to_text


SAMPLE_NOTE = NoteResult(
    title="Sample Note",
    summary="A short summary of the memo.",
    action_items=["Do thing one", "Do thing two"],
    key_topics=["topic-a", "topic-b"],
    raw_transcript="This is the raw transcript text.",
)

EMPTY_NOTE = NoteResult(
    title="Empty Note",
    summary="",
    action_items=[],
    key_topics=[],
    raw_transcript="",
)


def test_export_single_note_to_pdf_produces_bytes():
    pdf_bytes = export_notes_to_pdf([SAMPLE_NOTE])
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500


def test_export_batch_notes_to_pdf():
    pdf_bytes = export_notes_to_pdf([SAMPLE_NOTE, SAMPLE_NOTE, SAMPLE_NOTE])
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")


def test_export_handles_empty_note_gracefully():
    pdf_bytes = export_notes_to_pdf([EMPTY_NOTE])
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")


def test_export_to_text_contains_all_sections():
    text = export_note_to_text(SAMPLE_NOTE)
    assert "Sample Note" in text
    assert "A short summary of the memo." in text
    assert "Do thing one" in text
    assert "Do thing two" in text
    assert "topic-a" in text
    assert "This is the raw transcript text." in text


def test_export_to_text_handles_empty_note():
    text = export_note_to_text(EMPTY_NOTE)
    assert "no summary generated" in text
    assert "no action items identified" in text
