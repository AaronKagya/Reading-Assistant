import fitz
import pytest
from backend.pdf_processor import extract_pages
from backend.narration import preview_text

def test_extract_pdf(tmp_path):
    path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello from Reading Assistant")
    doc.save(path)
    doc.close()
    pages = extract_pages(str(path))
    assert pages[0]["page"] == 1
    assert "Hello from Reading Assistant" in preview_text(pages)

def test_reject_non_pdf(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("not a PDF")
    with pytest.raises(ValueError):
        extract_pages(str(path))
