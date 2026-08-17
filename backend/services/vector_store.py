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
DEFAULT_TOP_K = 3
MIN_SIMILARITY_SCORE = 0.35

index = faiss.IndexFlatIP(DIMENSION)
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

def replace_document(embeddings, chunk_objects, filename):
    """
    Replace all indexed chunks for a document with new chunks.
    """

    global index, chunks

    remaining_chunks = [
        chunk for chunk in chunks
        if chunk.filename != filename
    ]

    remaining_embeddings = []

    for i, chunk in enumerate(chunks):
        if chunk.filename != filename:
            remaining_embeddings.append(
                index.reconstruct(i)
            )

    new_vectors = np.array(embeddings).astype("float32")

    if remaining_embeddings:
        all_vectors = np.vstack([
            np.array(remaining_embeddings).astype("float32"),
            new_vectors,
        ])
    else:
        all_vectors = new_vectors

    index = faiss.IndexFlatIP(DIMENSION)
    index.add(all_vectors)

    chunks = remaining_chunks + chunk_objects

    save_index()
    save_chunks()

def total_vectors():
    return index.ntotal

def search(
    query_embedding,
    k: int = DEFAULT_TOP_K,
    min_similarity: float = MIN_SIMILARITY_SCORE,
):
    """
    Return up to k chunks that meet the minimum similarity score.
    """
    if index.ntotal == 0:
        return []

    query = np.array([query_embedding]).astype("float32")

    scores, indices = index.search(query, min(k, index.ntotal))

    results = []

    print("\n========== FAISS RESULTS ==========")

    for score, index_id in zip(scores[0], indices[0]):
        if index_id >= 0 and score >= min_similarity:
            chunk = chunks[index_id]

            print(
                f"score={score:.4f} | "
                f"{chunk.filename} | "
                f"chunk={chunk.chunk_index}"
            )

            results.append(chunk)

    print("========== END FAISS RESULTS ==========\n")

    return results

def debug_chunks():
    print("\n========== ALL INDEXED CHUNKS ==========")

    for chunk in chunks:
        if "Mathematics" in chunk.text or "Computer" in chunk.text:
            print(f"\n--- {chunk.filename} | chunk {chunk.chunk_index} ---")
            print(chunk.text)

    print("\n========== END DEBUG ==========\n")

# Load previously saved index and chunks when the application starts.
load_index()
load_chunks()
