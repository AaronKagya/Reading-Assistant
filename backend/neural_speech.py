"""Optional neural TTS proxy for a separately hosted OpenAI-compatible Kokoro service.

Keep neural inference off the free Render web process. Do not configure a public,
unmetered provider endpoint without authentication and rate limits.
"""
import os
import httpx
from fastapi import HTTPException, Header
from pydantic import BaseModel, Field

class NeuralSpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=800)
    voice: str = Field(default="af_heart", pattern=r"^[a-z]{2}_[a-z0-9_]+$")
    speed: float = Field(default=1.0, ge=0.7, le=1.3)

def neural_enabled() -> bool:
    return (os.getenv("ENABLE_NEURAL_TTS") == "1"
            and bool(os.getenv("KOKORO_API_URL", "").strip())
            and bool(os.getenv("KOKORO_API_KEY", "").strip())
            and bool(os.getenv("NEURAL_ACCESS_TOKEN", "").strip()))


def authorize_neural(access_token: str | None) -> None:
    import hmac
    if not neural_enabled():
        raise HTTPException(503, "Neural voice is not configured on this server yet")
    expected = os.environ["NEURAL_ACCESS_TOKEN"]
    if not access_token or not hmac.compare_digest(access_token, expected):
        raise HTTPException(403, "Neural voice requires a private beta access token")


async def synthesize_neural(request: NeuralSpeechRequest) -> bytes:
    base = os.getenv("KOKORO_API_URL", "").strip().rstrip("/")
    if not neural_enabled():
        raise HTTPException(503, "Neural voice is not configured on this server yet")
    if not base.startswith("https://") and not (os.getenv("ALLOW_LOCAL_KOKORO_HTTP") == "1" and base.startswith("http://127.0.0.1")):
        raise HTTPException(503, "Neural speech endpoint must use HTTPS")
    headers = {}
    token = os.getenv("KOKORO_API_KEY", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        async with httpx.AsyncClient(timeout=90, follow_redirects=False) as client:
            response = await client.post(
                base + "/v1/audio/speech",
                json={"model": "hexgrad/kokoro-82m", "input": request.text, "voice": request.voice,
                      "response_format": "wav", "speed": request.speed},
                headers=headers,
            )
        response.raise_for_status()
        if len(response.content) > 8 * 1024 * 1024:
            raise HTTPException(502, "Neural audio response too large")
        if not response.content:
            raise HTTPException(502, "Neural audio provider returned empty audio")
        return response.content
    except httpx.HTTPError as exc:
        raise HTTPException(502, "Neural voice provider unavailable") from exc
