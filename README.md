# 🎙️ Voice Notes → Action Items

Turn a rambling voice memo into a clean summary with clear action items — the kind of tool anyone leaving themselves audio notes would actually use.

## What it does

1. **Upload or record** a short audio clip directly in the browser
2. **Transcribes** it using the OpenAI Whisper API
3. **Summarizes** the transcript with GPT, extracting:
   - A short title
   - A concise summary
   - A checklist of clear action items
   - Key topics/tags
4. **Displays** everything in a simple, readable Streamlit UI

## Tech Stack

| Component        | Choice                     |
|-------------------|-----------------------------|
| Speech-to-text    | OpenAI Whisper API (`whisper-1`) |
| LLM               | OpenAI GPT (`gpt-4o-mini`) |
| UI                | Streamlit                  |

## Project Structure

```
voice-notes-to-action-items/
├── main.py                  # Streamlit app entry point (UI)
├── app/
│   ├── config.py             # Settings, API key loading
│   ├── transcription.py      # Whisper API wrapper
│   └── summarizer.py         # GPT summarization + action item extraction
├── tests/
│   └── test_summarizer.py    # Unit tests (mocked, no API calls)
├── sample_audio/             # Drop test audio clips here (gitignored)
├── .streamlit/config.toml    # Streamlit theme + upload size config
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd voice-notes-to-action-items
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add your OpenAI API key

Copy the example env file and fill in your key:

```bash
cp .env.example .env
```

Edit `.env`:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

Get a key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### 3. Run the app

```bash
streamlit run main.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

## Usage

1. Either **upload** an audio file (`mp3`, `mp4`, `wav`, `m4a`, `webm`, etc., up to 25 MB) or **record** directly in the browser using the microphone tab.
2. Click **"✨ Process Voice Note"**.
3. Read the generated title, summary, and check off action items as you go.
4. Expand **"Full transcript"** to see exactly what was transcribed.

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

Tests mock the OpenAI API so they run without a real key or network access.

## Notes & Limitations

- The OpenAI Whisper API has a hard 25 MB file size limit per request.
- Transcription quality depends on audio clarity — background noise and heavy accents can reduce accuracy.
- The app is stateless between sessions — nothing is saved to disk. Refreshing the page clears results.
- Costs: Whisper API is billed per minute of audio; GPT-4o-mini is billed per token. Both are inexpensive for short personal voice memos (a few cents per note).

## Possible Extensions (not implemented here)

- Batch-process multiple recordings at once
- Export results as PDF or shareable note
- Persist notes to a database
- Speaker diarization for multi-person recordings

## License

MIT — see [LICENSE](LICENSE).
