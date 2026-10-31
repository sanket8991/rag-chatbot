import uuid

from fastapi import APIRouter, HTTPException

from app.services.embedding_service import generate_session_embeddings

router = APIRouter()


@router.post("/{session_id}/embed")
def embed_documents(session_id: str):

    try:
        session_id = str(uuid.UUID(session_id))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID"
        )

    try:
        results = generate_session_embeddings(session_id)

        return {
            "message": "Embedding generation completed",
            "documents": results
        }

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))