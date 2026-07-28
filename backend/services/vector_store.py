import faiss
import numpy as np

DIMENSION = 384

index = faiss.IndexFlatL2(DIMENSION)


def add_embeddings(embeddings):
    """
    Add embedding vectors to the FAISS index.
    """
    vectors = np.array(embeddings).astype("float32")
    index.add(vectors)

def total_vectors():
    return index.ntotal

def search(query_embedding, k=3):
    """
    Search for the k most similar embeddings.
    """
    query = np.array([query_embedding]).astype("float32")
    distances, indices = index.search(query, k)
    return distances[0], indices[0]