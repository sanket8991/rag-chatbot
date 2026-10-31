import uuid

from fastapi import APIRouter, HTTPException

from app.services.qdrant_service import index_session_embeddings

router = APIRouter()


@router.post("/{session_id}/index")
def index_documents(session_id: str):

    try:
        session_id = str(uuid.UUID(session_id))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID"
        )

    try:
        results = index_session_embeddings(session_id)

        return {
            "message": "Documents indexed successfully in Qdrant",
            **results
        }

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))