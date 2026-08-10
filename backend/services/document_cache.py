from pathlib import Path
import hashlib
import pickle

DATA_DIR = Path("data/cache")
DATA_DIR.mkdir(parents=True, exist_ok=True)

CACHE_FILE = DATA_DIR / "document_cache.pkl"

document_cache = {}

def load_cache() -> None:
    """load
    Load the file from disk if it exists
    """

    global document_cache

    if CACHE_FILE.exists():
        with CACHE_FILE.open("rb") as file:
            document_cache = pickle.load(file)


def save_cache() -> None:
    """
    Save the file to disk.
    """
    with CACHE_FILE.open("wb") as file:
        pickle.dump(document_cache, file)


def compute_hash(file_path: Path) -> str:
    """
    Compute a SHA-256 hash for a document.
    """
    with file_path.open("rb") as file:
        content = file.read()

    hash_object = hashlib.sha256(content)
    return hash_object.hexdigest()


def is_document_changed(filename: str, file_hash: str) -> bool:
    stored_hash = document_cache.get(filename)

    if stored_hash is None:
        return True
    
    return stored_hash != file_hash

def document_exists(filename: str) -> bool:
    return filename in document_cache


def update_document(filename: str, file_hash: str) -> None:
    document_cache[filename] = file_hash
    save_cache()

load_cache()


