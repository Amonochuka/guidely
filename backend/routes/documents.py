from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.document_parser import extract_text
from services.chunking import chunk_text
from services.embeddings import generate_embedding
from services.vector_store import add_embeddings, total_vectors

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
        # Extract text
        text = extract_text(destination)

        # Split into chunks
        chunk_objects = chunk_text(text, file.filename)

        # Generate one embedding per chunk
        embeddings = [
            generate_embedding(chunk.text)
            for chunk in chunk_objects
        ]

        # Store vectors and metadata
        add_embeddings(embeddings, chunk_objects)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not process the uploaded document.",
        )

    return {
        "message": "File uploaded and indexed successfully",
        "filename": file.filename,
        "chunks_created": len(chunk_objects),
        "vectors_in_index": total_vectors(),
    }