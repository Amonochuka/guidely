from fastapi import APIRouter
from pydantic import BaseModel
from services.embeddings import generate_embedding
from services.vector_store import search as search_vectors

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


class SearchRequest(BaseModel):
    question: str


@router.post("/")
def search(request: SearchRequest):
    query_embedding = generate_embedding(request.question)

    results = search_vectors(query_embedding)
    return {
        "question": request.question,
        "matches": results,
    }