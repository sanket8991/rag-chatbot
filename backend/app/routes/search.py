import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.retrieval_service import search_session_documents

router = APIRouter()


class SearchRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)


@router.post("/{session_id}/search")
def search_documents(session_id: str, request: SearchRequest):

    try:
        session_id = str(uuid.UUID(session_id))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID"
        )

    try:
        results = search_session_documents(
            session_id=session_id,
            question=request.question.strip(),
            top_k=request.top_k
        )

        return {
            "question": request.question,
            "total_results": len(results),
            "results": results
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )