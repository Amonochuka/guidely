from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.document_parser import extract_text
from services.chunking import chunk_text
from services.embeddings import generate_embedding
from services.vector_store import (
    add_embeddings,
    list_documents,
    replace_document,
    total_vectors,
)
from services.document_cache import (
    compute_hash,
    is_document_changed,
    document_exists,
    update_document,
)
from services.logger import logger
from services.metrics import (
    record_cache_hit,
    record_cache_miss,
    record_embeddings_generated,
    record_failure,
)


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
    documents = list_documents()

    return {
        "documents": documents,
        "total_documents": len(documents),
    }


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name

    if not filename:
        record_failure("invalid_filename")

        raise HTTPException(
            status_code=400,
            detail="A valid filename is required.",
        )

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        record_failure("unsupported_file_type")

        raise HTTPException(
            status_code=400,
            detail="Only .txt, .pdf and .docx files are allowed.",
        )

    content = await file.read()

    if not content:
        record_failure("empty_document")

        raise HTTPException(
            status_code=400,
            detail="The uploaded document is empty.",
        )

    destination = UPLOAD_DIR / filename

    with destination.open("wb") as buffer:
        buffer.write(content)

    logger.info(f"Received upload: {filename}")

    file_hash = compute_hash(destination)

    # Skip re-indexing when the same document has already been indexed
    # and its contents have not changed.
    if not is_document_changed(filename, file_hash):
        logger.info(
            f"Cache hit: {filename}. "
            "Document unchanged; skipping re-indexing."
        )

        record_cache_hit()

        return {
            "message": "Document already indexed. Skipping re-indexing.",
            "filename": filename,
            "vectors_in_index": total_vectors(),
        }

    record_cache_miss()

    try:
        # Extract text
        text = extract_text(destination)

        if not text.strip():
            raise ValueError("Document contains no extractable text.")

        # Split into chunks
        chunk_objects = chunk_text(
            text,
            filename,
        )

        # Generate one embedding per chunk
        embeddings = [
            generate_embedding(chunk.text)
            for chunk in chunk_objects
        ]
        record_embeddings_generated(len(embeddings))

        # Replace existing vectors when this filename already exists.
        # Otherwise add the new document to the index.
        if document_exists(filename):
            replace_document(
                embeddings,
                chunk_objects,
                filename,
            )
        else:
            add_embeddings(
                embeddings,
                chunk_objects,
            )

        # Update cache only after successful indexing
        update_document(
            filename,
            file_hash,
        )

        logger.info(
            f"Indexed {len(chunk_objects)} chunks from "
            f"{filename}"
        )

    except Exception:
        record_failure("document_processing")

        logger.exception(
            f"Failed to process document: {filename}"
        )

        raise HTTPException(
            status_code=400,
            detail="Could not process the uploaded document.",
        )

    return {
        "message": "File uploaded and indexed successfully",
        "filename": filename,
        "chunks_created": len(chunk_objects),
        "vectors_in_index": total_vectors(),
    }
