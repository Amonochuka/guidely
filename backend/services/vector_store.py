import faiss
import numpy as np
from models.chunk import Chunk

DIMENSION = 384

index = faiss.IndexFlatL2(DIMENSION)
chunks: list[Chunk] = []


def add_embeddings(embeddings,chunk_objects) :
    """
    Add embedding vectors to the FAISS index.
    """
    vectors = np.array(embeddings).astype("float32")
    index.add(vectors)
    chunks.extend(chunk_objects)

def total_vectors():
    return index.ntotal

def search(query_embedding, k=3):
    """
    Search for the k most similar embeddings.
    """
    query = np.array([query_embedding]).astype("float32")
    distances, indices = index.search(query, k)
    results = []

    for index_id in indices[0]:
        if index_id >= 0:
            results.append(chunks[index_id])

    return results