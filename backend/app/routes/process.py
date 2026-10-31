import uuid

from fastapi import APIRouter, HTTPException

from app.services.pdf_extractor import extract_session_pdfs

router = APIRouter()


@router.post("/{session_id}/extract")
async def extract_pdfs(session_id: str):

    try:
        session_id = str(uuid.UUID(session_id))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID"
        )

    try:
        results = extract_session_pdfs(session_id)

        return {
            "message": "PDF text extraction completed",
            "documents": results,
        }

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))