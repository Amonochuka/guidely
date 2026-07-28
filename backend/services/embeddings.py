from sentence_transformers import SentenceTransformer

# Load the model once when the application starts
model = SentenceTransformer("all-MiniLM-L6-v2")
def generate_embedding(text: str):
    """
    Generate an embedding vector for a piece of text.
    """
    return model.encode(text).tolist()