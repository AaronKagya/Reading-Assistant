from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_neural_disabled_by_default(monkeypatch):
    monkeypatch.delenv("ENABLE_NEURAL_TTS", raising=False)
    monkeypatch.delenv("KOKORO_API_URL", raising=False)
    assert client.get("/neural-status").json() == {"enabled": False, "requires_access_token": True}
    response = client.post("/neural-speech", json={"text": "Hello there."})
    assert response.status_code == 503

def test_neural_request_limits():
    assert client.post("/neural-speech", json={"text": "x" * 801}).status_code == 422
    assert client.post("/neural-speech", json={"text": "Hello", "speed": 3}).status_code == 422
    assert client.post("/neural-speech", json={"text": "Hello", "voice": "../unsafe"}).status_code == 422

def test_neural_requires_private_token(monkeypatch):
    monkeypatch.setenv("ENABLE_NEURAL_TTS", "1")
    monkeypatch.setenv("KOKORO_API_URL", "https://api.fastinfra.ai")
    monkeypatch.setenv("KOKORO_API_KEY", "test-provider-key")
    monkeypatch.setenv("NEURAL_ACCESS_TOKEN", "private-beta-token")
    response = client.post("/neural-speech", json={"text": "Hello"})
    assert response.status_code == 403
