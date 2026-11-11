import io
import fitz
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def make_pdf():
    doc = fitz.open()
    for text in ("Chapter one: A short introduction.", "Chapter two: Another page."):
        page = doc.new_page()
        page.insert_text((72, 72), text)
    payload = doc.tobytes()
    doc.close()
    return payload

def test_document_text_returns_every_readable_page():
    response = client.post("/document-text", files={"file": ("book.pdf", make_pdf(), "application/pdf")})
    assert response.status_code == 200
    body = response.json()
    assert body["pages_with_text"] == 2
    assert [page["page"] for page in body["pages"]] == [1, 2]
    assert "Chapter two" in body["pages"][1]["text"]

def test_document_text_rejects_invalid_pdf():
    response = client.post("/document-text", files={"file": ("book.pdf", b"invalid", "application/pdf")})
    assert response.status_code == 400

def test_health():
    assert client.get("/health").json() == {"status": "ok"}
