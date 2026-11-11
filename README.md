# Reading Assistant 2.0

Premium PDF-to-audio narration built on the original speech-synthesis research notebook.

## Status
Early MVP: PDF extraction and ElevenLabs audio preview API. Original notebook remains unchanged.

## Quick start
Python 3.11+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ELEVENLABS_API_KEY="your-key"
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000/docs.

- `GET /health`: service health
- `POST /preview-text`: upload PDF, extract text preview
- `POST /preview-audio`: upload PDF and authorized `voice_id`, return MP3

Audio generation consumes provider credits. Limits: 15 MB, 300 pages, selectable text only. Scanned and password-protected PDFs are not supported yet. Do not deploy publicly without authentication, rate limiting, and privacy safeguards.

## Tests
```bash
pytest -q
```

## Roadmap
Chapter segmentation, async jobs, responsive reader, narration modes, caching, cost controls, storage and deletion.

## Research
`reading_assistant.ipynb` is the original LJSpeech/PyTorch experiment and remains untouched.

## Tutor reading mode
Set both `OPENAI_API_KEY` and `ELEVENLABS_API_KEY` as environment variables. Optionally set `TUTOR_MODEL` (default `gpt-4o-mini`). Do not commit credentials. `POST /tutor-preview-text` accepts a PDF and returns the source excerpt and tutor script. `POST /tutor-preview-audio` accepts a PDF and ElevenLabs `voice_id` as multipart form fields and returns MP3. The first version uses only a short excerpt, not a complete PDF. Review tutor explanations against the source: automated rewriting can introduce errors. Each generation may incur API costs.
