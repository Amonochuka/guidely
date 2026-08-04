import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.embeddings import generate_embedding
from services.vector_store import search as search_vectors
from services.gemini import generate_answer
from services.logger import logger
from services.metrics import record_query

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


class SearchRequest(BaseModel):
    question: str


@router.post("/")
def search(request: SearchRequest): 
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="User must provide a question.",
        )

    logger.info(f"Question received: {request.question}")

    start_time = time.perf_counter()

    query_embedding = generate_embedding(request.question)

    results = search_vectors(query_embedding)
    if not results:
        logger.warning(
            f"No relevant documents found for question: {request.question}"
        )
        
        raise HTTPException(
            status_code=404,
            detail="No relevant documents found.",
        )


    context = "\n\n".join(
        " ".join(chunk.text.split())
        for chunk in results
    )

    prompt = f"""
You are a helpful assistant answering questions about uploaded documents.

Answer using only the provided context.

If the answer is present, answer it directly and briefly explain your answer using the relevant information from the context.

Do not mention "the context" or "the document."

If the answer is not present, reply exactly:

"I couldn't find that information in the uploaded documents."

Context:
{context}

Question:
{request.question}
"""

    try:
        answer = generate_answer(prompt)
    except Exception:
        logger.exception("Gemini failed to generate answer")

        raise HTTPException(
            status_code=502,
            detail="Failed to generate an answer from the AI model.",
        )
        
    logger.info(
        f"Answered question using {len(results)} chunks."
    )

    elapsed = time.perf_counter() - start_time

    record_query(elapsed)

    logger.info(
        f"Search completed in {elapsed:.2f} seconds."
    )

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