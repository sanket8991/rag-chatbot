import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.retrieval_service import search_session_documents
from app.services.llm_service import generate_answer

router = APIRouter()


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)


@router.post("/{session_id}/ask")
def ask_documents(session_id: str, request: AskRequest):

    try:
        session_id = str(uuid.UUID(session_id))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID"
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        # Step 1: Retrieve relevant PDF chunks
        retrieved_chunks = search_session_documents(
            session_id=session_id,
            question=question,
            top_k=request.top_k
        )

        if not retrieved_chunks:
            return {
                "question": question,
                "answer": "I could not find relevant information in the uploaded documents.",
                "sources": [],
                "retrieved_chunks": 0
            }

        # Step 2: Generate an answer using OpenAI
        answer = generate_answer(
            question=question,
            retrieved_chunks=retrieved_chunks
        )

        # Step 3: Prepare source information
        sources = []
        seen_sources = set()

        for chunk in retrieved_chunks:

            document_id = chunk.get("document_id")

            # Fall back to filename for older indexed records
            source_key = (
                document_id or chunk.get("filename"),
                chunk.get("page_number")
            )

            if source_key not in seen_sources:
                seen_sources.add(source_key)

                sources.append({
                    "document_id": document_id,
                    "filename": chunk.get("filename"),
                    "stored_filename": chunk.get("stored_filename"),
                    "page_number": chunk.get("page_number"),
                    "relevance_score": chunk.get("score")
                })

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": len(retrieved_chunks)
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )