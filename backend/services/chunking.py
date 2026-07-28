from typing import List
from models.chunk import Chunk

def chunk_text(text: str,  filename: str,  chunk_size: int = 500) -> List[Chunk]:
    """
    Split text into fixed-size chunks.
    """

    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]

        if chunk.strip():
            chunks.append(
                Chunk(
                    chunk_id=len(chunks),
                    filename=filename,
                    chunk_index=len(chunks),
                    text=chunk,
                )
            )

    return chunks