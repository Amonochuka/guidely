from typing import List
from models.chunk import Chunk


def chunk_text(
    text: str,
    filename: str,
    chunk_size: int = 800,
    overlap: int = 200,
) -> List[Chunk]:
    """
    Split text into overlapping chunks.
    """

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(
                Chunk(
                    chunk_id=len(chunks),
                    filename=filename,
                    chunk_index=len(chunks),
                    text=chunk,
                )
            )

        start += chunk_size - overlap

    return chunks