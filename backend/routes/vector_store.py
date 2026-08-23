from fastapi import APIRouter, HTTPException

from services import vector_store
from services.logger import logger


router = APIRouter(
    prefix="/vector-store",
    tags=["Vector Store"],
)


@router.get("/")
def get_embeddings(filename: str | None = None):
    """
    Return stored embeddings so they can be inspected or reused
    for similarity-search operations.
    """
    embeddings = []

    for position, chunk in enumerate(vector_store.chunks):
        if filename and chunk.filename != filename:
            continue

        embeddings.append(
            {
                "filename": chunk.filename,
                "chunk": chunk.chunk_index,
                "text_preview": " ".join(chunk.text.split())[:200],
                "embedding": vector_store.index.reconstruct(position).tolist(),
            }
        )

    return {
        "total_vectors": vector_store.index.ntotal,
        "dimension": vector_store.index.d,
        "embeddings": embeddings,
    }


@router.post("/persist")
def persist_vectors():
    """
    Persist generated embeddings to the vector database on disk.
    """
    try:
        vector_store.save_index()
        vector_store.save_chunks()

    except OSError:
        logger.exception("Failed to persist vector store")

        raise HTTPException(
            status_code=500,
            detail="Could not persist the vector store to disk.",
        )

    logger.info(
        f"Persisted {vector_store.index.ntotal} vectors to disk"
    )

    return {
        "message": "Vector store persisted successfully.",
        "vectors_in_index": vector_store.index.ntotal,
        "chunks_stored": len(vector_store.chunks),
    }
