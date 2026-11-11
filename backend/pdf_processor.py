from pathlib import Path
import fitz

MAX_PAGES = 300

def extract_pages(pdf_path: str) -> list[dict]:
    path = Path(pdf_path)
    if not path.is_file() or path.suffix.lower() != ".pdf":
        raise ValueError("A PDF file is required")
    pages = []
    try:
        with fitz.open(path) as document:
            if document.needs_pass:
                raise ValueError("Password-protected PDFs are not supported")
            if document.page_count > MAX_PAGES:
                raise ValueError(f"PDF exceeds {MAX_PAGES} pages")
            for number, page in enumerate(document, start=1):
                text = page.get_text("text", sort=True).strip()
                if text:
                    pages.append({"page": number, "text": text})
    except (fitz.FileDataError, fitz.EmptyFileError) as exc:
        raise ValueError("Invalid or damaged PDF") from exc
    if not pages:
        raise ValueError("No selectable text found; scanned PDFs require OCR")
    return pages
