import pytest
from backend.tutor import select_source, explain_as_tutor

def test_select_source():
    pages = [{"page": 1, "text": "Machine learning learns from examples. " * 80}]
    result = select_source(pages)
    assert result.startswith("Machine learning")
    assert len(result) <= 1800

def test_empty_source():
    with pytest.raises(ValueError):
        select_source([{"page": 1, "text": "   "}])

@pytest.mark.asyncio
async def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        await explain_as_tutor("A valid excerpt")
