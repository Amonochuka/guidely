from fastapi import APIRouter
from pydantic import BaseModel
from services.embeddings import generate_embedding
from services.vector_store import search as search_vectors
from services.gemini import generate_answer

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

    context = "\n\n".join(
        " ".join(chunk.text.split())
        for chunk in results
    )

    prompt = f"""
You are a helpful assistant.

Answer the user's question ONLY using the provided context.

If the answer cannot be found in the context, say:
"I couldn't find that information in the uploaded documents."

Context:
{context}

Question:
{request.question}
"""

    answer = generate_answer(prompt)

    sources = []
    for chunk in results:
        sources.append(
            {
                "filename":chunk.filename,
                "snippet": " ".join(chunk.text.split())[:200],
                "chunk":chunk.chunk_index
            }
        )

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources,
    }