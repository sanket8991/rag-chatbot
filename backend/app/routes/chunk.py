import uuid

from fastapi import APIRouter, HTTPException

from app.services.chunker import chunk_session_documents

router = APIRouter()


@router.post("/{session_id}/chunk")
async def chunk_documents(session_id: str):

    try:
        session_id = str(uuid.UUID(session_id))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID"
        )

    try:
        results = chunk_session_documents(session_id)

        return {
            "message": "Document chunking completed",
            "documents": results
        }

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))