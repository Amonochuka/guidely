from typing import List
from models.chunk import Chunk


def chunk_text(
    text: str,
    filename: str,
    chunk_size: int = 600,
    overlap: int = 100,
) -> List[Chunk]:
    """
    Split text into overlapping word chunks.

    A 600-word chunk is roughly within the 500--1,000-token target for
    typical English documents. Splitting on words also avoids cutting a word
    or sentence token in half.
    """
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and greater than overlap.")

    words = text.split()
    chunks = []

    for start in range(0, len(words), chunk_size - overlap):
        chunk_words = words[start : start + chunk_size]
        if not chunk_words:
            continue

        chunks.append(
            Chunk(
                chunk_id=len(chunks),
                filename=filename,
                chunk_index=len(chunks),
                text=" ".join(chunk_words),
            )
        )

        if start + chunk_size >= len(words):
            break

    return chunks
