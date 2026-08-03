import faiss
import numpy as np
from pathlib import Path
import pickle
from models.chunk import Chunk

DATA_DIR = Path("data/faiss")
DATA_DIR.mkdir(parents=True, exist_ok=True)

INDEX_FILE = DATA_DIR / "index.faiss"
CHUNKS_FILE = DATA_DIR / "chunks.pkl"

DIMENSION = 384

index = faiss.IndexFlatL2(DIMENSION)
chunks: list[Chunk] = []


def save_index():
    """
    Save the FAISS index to disk
    """
    faiss.write_index(index, str(INDEX_FILE))

def load_index():
    """
    Load the FAISS index from disk if it exists
    """
    global index

    if INDEX_FILE.exists():
        index = faiss.read_index(str(INDEX_FILE))

def save_chunks():
    """
    Save the chunks to disk.
    """
    with CHUNKS_FILE.open("wb") as file:
        pickle.dump(chunks, file)

def load_chunks():
    """
    Load the chunks from disk if they exist
    """
    global chunks

    if CHUNKS_FILE.exists():
        with CHUNKS_FILE.open("rb") as file:
            chunks = pickle.load(file)

def add_embeddings(embeddings, chunk_objects):
    """
    Add embedding vectors to the FAISS index.
    """
    vectors = np.array(embeddings).astype("float32")
    index.add(vectors)
    chunks.extend(chunk_objects)
    save_index()
    save_chunks()

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

# Load previously saved index and chunks when the application starts.
load_index()
load_chunks()