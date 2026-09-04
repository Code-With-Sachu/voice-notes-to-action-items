"""
Unit tests for app.summarizer. Uses mocking so no real API calls are made.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from app.summarizer import summarize_transcript, SummarizationError, NoteResult


def _mock_openai_response(payload: dict):
    """Builds a mock OpenAI chat completion response object."""
    mock_message = MagicMock()
    mock_message.content = json.dumps(payload)
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


@patch("app.summarizer.OPENAI_API_KEY", "fake-key")
@patch("app.summarizer.OpenAI")
def test_summarize_transcript_success(mock_openai_cls):
    payload = {
        "title": "Weekly Planning Notes",
        "summary": "Discussed upcoming deadlines and team priorities.",
        "action_items": ["Email Sarah about the budget", "Schedule design review"],
        "key_topics": ["planning", "budget", "design"],
    }
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _mock_openai_response(payload)
    mock_openai_cls.return_value = mock_client

    result = summarize_transcript("some rambling transcript text")

    assert isinstance(result, NoteResult)
    assert result.title == "Weekly Planning Notes"
    assert len(result.action_items) == 2
    assert "planning" in result.key_topics
    assert result.raw_transcript == "some rambling transcript text"


@patch("app.summarizer.OPENAI_API_KEY", "fake-key")
@patch("app.summarizer.OpenAI")
def test_summarize_transcript_empty_action_items(mock_openai_cls):
    payload = {
        "title": "Casual Ramble",
        "summary": "Just thinking out loud, no concrete tasks.",
        "action_items": [],
        "key_topics": [],
    }
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _mock_openai_response(payload)
    mock_openai_cls.return_value = mock_client

    result = summarize_transcript("just rambling with no real tasks")
    assert result.action_items == []


@patch("app.summarizer.OPENAI_API_KEY", "")
def test_summarize_transcript_missing_api_key():
    with pytest.raises(SummarizationError, match="API key is not configured"):
        summarize_transcript("some transcript")


@patch("app.summarizer.OPENAI_API_KEY", "fake-key")
def test_summarize_transcript_empty_input():
    with pytest.raises(SummarizationError, match="empty transcript"):
        summarize_transcript("   ")


@patch("app.summarizer.OPENAI_API_KEY", "fake-key")
@patch("app.summarizer.OpenAI")
def test_summarize_transcript_invalid_json(mock_openai_cls):
    mock_message = MagicMock()
    mock_message.content = "not valid json {{"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_cls.return_value = mock_client

    with pytest.raises(SummarizationError, match="Could not parse"):
        summarize_transcript("some transcript")
