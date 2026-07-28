from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from services.document_parser import extract_text
from services.chunking import chunk_text

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

# Folder where uploaded files will be stored
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}


@router.get("/")
def documents_home():
    return {"message": "Documents endpoint"}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .txt, .pdf and .docx files are allowed.",
        )

    destination = UPLOAD_DIR / file.filename

    with destination.open("wb") as buffer:
        buffer.write(await file.read())

    try:
        text = extract_text(destination)
        chunks = chunk_text(text)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from the uploaded document.",
        )

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "chunks": len(chunks),
        "first_chunk": chunks[0] if chunks else None,
    }