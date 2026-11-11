import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile, Form, Header
from fastapi.responses import Response, FileResponse
from .pdf_processor import extract_pages
from .narration import preview_text, synthesize
from .tutor import select_source, explain_as_tutor
from .neural_speech import NeuralSpeechRequest, synthesize_neural, neural_enabled, authorize_neural

app = FastAPI(title="Reading Assistant API", version="0.1.0")

@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def reader_home():
    return FileResponse(Path(__file__).resolve().parent.parent / "frontend" / "index.html")
MAX_UPLOAD_BYTES = 15 * 1024 * 1024

async def read_pdf(upload: UploadFile) -> list[dict]:
    if not upload.filename or not upload.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Upload a PDF file")
    data = await upload.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "PDF exceeds 15 MB")
    if not data.startswith(b"%PDF-"):
        raise HTTPException(400, "File is not a valid PDF")
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "upload.pdf"
        path.write_bytes(data)
        try:
            return extract_pages(str(path))
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/document-text")
async def document_text_endpoint(file: UploadFile = File(...)):
    """Return selectable PDF text by page for client-side narration.

    No PDF content is persisted after extraction.
    """
    pages = await read_pdf(file)
    return {"pages": pages, "pages_with_text": len(pages)}

@app.post("/preview-text")
async def preview_text_endpoint(file: UploadFile = File(...)):
    pages = await read_pdf(file)
    return {"pages_with_text": len(pages), "preview": preview_text(pages)}

@app.post("/preview-audio")
async def preview_audio_endpoint(file: UploadFile = File(...), voice_id: str = Form(...)):
    pages = await read_pdf(file)
    try:
        audio = await synthesize(preview_text(pages), voice_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    except Exception:
        raise HTTPException(502, "Speech provider request failed")
    return Response(content=audio, media_type="audio/mpeg", headers={"Content-Disposition": 'attachment; filename="preview.mp3"'})

@app.post("/tutor-preview-text")
async def tutor_preview_text(file: UploadFile = File(...)):
    pages = await read_pdf(file)
    source = select_source(pages)
    try:
        explanation = await explain_as_tutor(source)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    except Exception:
        raise HTTPException(502, "Tutor provider request failed")
    return {"source_excerpt": source, "tutor_script": explanation, "mode": "tutor"}

@app.post("/tutor-preview-audio")
async def tutor_preview_audio(file: UploadFile = File(...), voice_id: str = Form(...)):
    pages = await read_pdf(file)
    source = select_source(pages)
    try:
        explanation = await explain_as_tutor(source)
        audio = await synthesize(explanation, voice_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    except Exception:
        raise HTTPException(502, "Tutor or speech provider request failed")
    return Response(content=audio, media_type="audio/mpeg", headers={"Content-Disposition": 'attachment; filename="tutor-preview.mp3"'})

@app.get("/neural-status")
def neural_status():
    return {"enabled": neural_enabled(), "requires_access_token": True}

@app.post("/neural-speech")
async def neural_speech_endpoint(request: NeuralSpeechRequest, x_neural_access_token: str | None = Header(default=None)):
    authorize_neural(x_neural_access_token)
    audio = await synthesize_neural(request)
    return Response(content=audio, media_type="audio/wav", headers={"Cache-Control": "no-store"})
