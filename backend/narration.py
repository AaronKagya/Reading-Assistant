import os
import re
import httpx

MAX_CHARS = 3000

def preview_text(pages: list[dict], max_chars: int = 700) -> str:
    text = " ".join(" ".join(page["text"].split()) for page in pages)
    if not text.strip():
        raise ValueError("No text to narrate")
    return text[:max_chars].rsplit(" ", 1)[0] or text[:max_chars]

async def synthesize(text: str, voice_id: str) -> bytes:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is not configured")
    if not text.strip() or len(text) > MAX_CHARS:
        raise ValueError(f"Text must contain 1-{MAX_CHARS} characters")
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,100}", voice_id):
        raise ValueError("Invalid voice ID")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(
            url,
            headers={"xi-api-key": api_key, "Accept": "audio/mpeg"},
            params={"output_format": "mp3_44100_128"},
            json={"text": text, "model_id": os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")},
        )
        response.raise_for_status()
        return response.content
