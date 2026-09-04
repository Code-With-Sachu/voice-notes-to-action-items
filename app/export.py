"""
Export a NoteResult (or a batch of them) as a PDF or plain-text file.
Used for the stretch goal: batch processing + exportable notes.
"""

from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from app.summarizer import NoteResult


def _clean(text: str) -> str:
    """
    fpdf2's core fonts (Helvetica) only support latin-1. Replace common
    "smart" punctuation with plain ASCII so encoding never breaks the export.
    """
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\u2026": "...",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text.encode("latin-1", "replace").decode("latin-1")


class NotePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, _clean("Voice Notes -> Action Items"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(200, 200, 200)
        self.line(10, 20, 200, 20)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def _add_note_to_pdf(pdf: NotePDF, note: NoteResult, include_transcript: bool = True):
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(20, 60, 120)
    pdf.multi_cell(0, 8, _clean(note.title))
    pdf.ln(2)

    # Timestamp
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, datetime.now().strftime("Generated %B %d, %Y at %I:%M %p"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # Summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, "Summary", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, _clean(note.summary) if note.summary else "(no summary generated)")
    pdf.ln(4)

    # Action items
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Action Items", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 11)
    if note.action_items:
        for item in note.action_items:
            pdf.set_x(14)
            pdf.multi_cell(0, 6, _clean(f"[ ] {item}"))
    else:
        pdf.multi_cell(0, 6, "(no action items identified)")
    pdf.ln(4)

    # Key topics
    if note.key_topics:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Topics", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, _clean(", ".join(note.key_topics)))
        pdf.ln(4)

    # Full transcript
    if include_transcript and note.raw_transcript:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Full Transcript", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(90, 90, 90)
        pdf.multi_cell(0, 5, _clean(note.raw_transcript))


def export_notes_to_pdf(notes: list[NoteResult], include_transcript: bool = True) -> bytes:
    """
    Build a PDF from one or more NoteResults and return it as bytes,
    ready to hand to st.download_button.
    """
    pdf = NotePDF()
    pdf.set_auto_page_break(auto=True, margin=18)

    for note in notes:
        _add_note_to_pdf(pdf, note, include_transcript=include_transcript)

    output = pdf.output()
    return bytes(output)


def export_note_to_text(note: NoteResult) -> str:
    """Build a simple plain-text version of a single note (for quick copy/share)."""
    lines = [
        note.title,
        "=" * len(note.title),
        "",
        "SUMMARY",
        "-------",
        note.summary or "(no summary generated)",
        "",
        "ACTION ITEMS",
        "------------",
    ]
    if note.action_items:
        lines += [f"[ ] {item}" for item in note.action_items]
    else:
        lines.append("(no action items identified)")

    if note.key_topics:
        lines += ["", "TOPICS", "------", ", ".join(note.key_topics)]

    lines += ["", "FULL TRANSCRIPT", "---------------", note.raw_transcript or ""]

    return "\n".join(lines)
