"""
Summarization: turns a raw transcript into a title, summary, and action items
using the OpenAI Chat Completions API with structured JSON output.
"""

import json
from dataclasses import dataclass, field

from openai import OpenAI, OpenAIError

from app.config import OPENAI_API_KEY, SUMMARY_MODEL


class SummarizationError(Exception):
    """Raised when summarization fails."""
    pass


@dataclass
class NoteResult:
    """Structured result of processing a voice note."""
    title: str
    summary: str
    action_items: list[str] = field(default_factory=list)
    key_topics: list[str] = field(default_factory=list)
    raw_transcript: str = ""


SYSTEM_PROMPT = """You are an assistant that turns rambling voice memo transcripts \
into clean, useful notes. Given a transcript, produce:

1. A short descriptive title (5-8 words)
2. A concise summary (2-4 sentences) capturing the key points
3. A list of clear, actionable action items (imperative form, e.g. "Email Sarah about the budget"). \
If there are no real action items, return an empty list — do not invent tasks.
4. A short list of key topics/tags mentioned (single words or short phrases)

Respond ONLY with valid JSON in this exact shape, no markdown fences, no extra text:
{
  "title": "...",
  "summary": "...",
  "action_items": ["...", "..."],
  "key_topics": ["...", "..."]
}"""


def summarize_transcript(transcript: str) -> NoteResult:
    """
    Sends a transcript to the LLM and returns a structured NoteResult.

    Args:
        transcript: The raw transcribed text.

    Returns:
        A NoteResult with title, summary, action items, and topics.

    Raises:
        SummarizationError: If the API key is missing or the API call/parsing fails.
    """
    if not OPENAI_API_KEY:
        raise SummarizationError(
            "OpenAI API key is not configured. Set OPENAI_API_KEY in your environment "
            "or .env file."
        )

    if not transcript.strip():
        raise SummarizationError("Cannot summarize an empty transcript.")

    client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model=SUMMARY_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Transcript:\n\n{transcript}"},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
    except OpenAIError as e:
        raise SummarizationError(f"Summarization failed: {e}") from e

    content = response.choices[0].message.content

    try:
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError) as e:
        raise SummarizationError(f"Could not parse model response as JSON: {e}") from e

    return NoteResult(
        title=data.get("title", "Untitled Note").strip(),
        summary=data.get("summary", "").strip(),
        action_items=[str(item).strip() for item in data.get("action_items", []) if str(item).strip()],
        key_topics=[str(topic).strip() for topic in data.get("key_topics", []) if str(topic).strip()],
        raw_transcript=transcript,
    )
