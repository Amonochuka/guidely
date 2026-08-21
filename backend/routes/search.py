import time

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.embeddings import generate_embedding
from services.vector_store import search_ranked
from services.gemini import GeminiConfigurationError, generate_answer
from services.logger import logger
from services.metrics import record_failure, record_query


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


class SearchRequest(BaseModel):
    question: str


@router.post("/")
def search(request: SearchRequest):
    if not request.question.strip():
        record_failure("empty_query")

        raise HTTPException(
            status_code=400,
            detail="User must provide a question.",
        )

    logger.info(
        f"Question received: {request.question}"
    )

    start_time = time.perf_counter()

    # Generate query embedding
    embedding_start = time.perf_counter()

    query_embedding = generate_embedding(
        request.question
    )

    embedding_time = (
        time.perf_counter() - embedding_start
    )

    # Search FAISS
    search_start = time.perf_counter()

    ranked_results = search_ranked(query_embedding)

    search_time = (
        time.perf_counter() - search_start
    )

    if not ranked_results:
        record_failure("no_relevant_results")

        logger.warning(
            "No relevant documents found for question: "
            f"{request.question}"
        )

        raise HTTPException(
            status_code=404,
            detail="No documents have been indexed yet. Upload a document first.",
        )

    # Build context for Gemini
    context = "\n\n".join(
        " ".join(chunk.text.split())
        for chunk, _ in ranked_results
    )

    prompt = f"""
You are answering a question about a person's uploaded documents.

The answer MUST be based only on the DOCUMENT EXCERPTS.

DOCUMENT EXCERPTS:
{context}

QUESTION:
{request.question}

Follow these rules:

1. Read the document excerpts carefully.
2. If the excerpts contain a fact that answers the question, answer YES/NO or give the requested fact directly.
3. You are allowed to interpret obvious equivalent wording.
4. "BSc" means "Bachelor of Science".
5. A Bachelor of Science is a bachelor's degree.
6. If a document says someone has a "BSc" followed by a subject, treat that as evidence that the person has a bachelor's degree.
7. Do NOT require the document to literally contain the words "bachelor's degree".
8. Do NOT say the information is missing when the excerpts contain equivalent evidence.
9. Do NOT invent facts that are not supported by the excerpts.
10. If the excerpts genuinely contain no information that answers the question, reply exactly:
"I couldn't find that information in the uploaded documents."

For example, if the excerpts say:

"Qualification: BSc Mathematics / Computer Science (Statistics)"

and the question asks:

"Does Amon have a bachelor's degree?"

the correct answer is:

"Yes. Amon has a BSc in Mathematics / Computer Science (Statistics), which is a Bachelor of Science degree."

Now answer the QUESTION using the DOCUMENT EXCERPTS.

ANSWER:
"""

    # Generate answer
    generation_start = time.perf_counter()

    try:
        answer = generate_answer(prompt)

    except GeminiConfigurationError as error:
        record_failure("missing_model_key")
        logger.warning("Gemini configuration error: %s", error)
        raise HTTPException(status_code=503, detail=str(error))

    except (TimeoutError, httpx.TimeoutException):
        record_failure("answer_generation_timeout")
        logger.exception("Gemini request timed out")
        raise HTTPException(
            status_code=504,
            detail="The AI service timed out. Please try again.",
        )

    except Exception:
        record_failure("answer_generation")

        logger.exception(
            "Gemini failed to generate answer"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Failed to generate an answer "
                "from the AI model."
            ),
        )

    generation_time = (
        time.perf_counter() - generation_start
    )

    logger.info(
        f"Answered question using {len(ranked_results)} chunks."
    )

    elapsed = (
        time.perf_counter() - start_time
    )

    record_query(elapsed)

    logger.info(
        f"Embedding: {embedding_time:.2f}s | "
        f"FAISS: {search_time:.2f}s | "
        f"Gemini: {generation_time:.2f}s | "
        f"Total: {elapsed:.2f}s"
    )

    # Build source information
    sources = []

    for rank, (chunk, score) in enumerate(ranked_results, start=1):
        sources.append(
            {
                "filename": chunk.filename,
                "snippet": " ".join(
                    chunk.text.split()
                )[:200],
                "chunk": chunk.chunk_index,
                "rank": rank,
                "similarity_score": round(score, 3),
            }
        )

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources,
    }
