
import os
import uuid
import json
import fitz

from fastapi import APIRouter, UploadFile, File
from typing import List

router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):

    session_id = str(uuid.uuid4())

    session_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    uploaded_documents = []
    rejected_documents = []
    document_metadata = {}

    for file in files:

        original_filename = os.path.basename(
            file.filename or "unnamed.pdf"
        )

        if not original_filename.lower().endswith(".pdf"):
            rejected_documents.append({
                "filename": original_filename,
                "reason": "Only PDF files are allowed."
            })
            continue

        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}.pdf"
        file_path = os.path.join(session_dir, safe_filename)

        try:
            content = await file.read()

            if not content:
                raise ValueError("Empty file.")

            pdf_document = fitz.open(
                stream=content,
                filetype="pdf"
            )

            if pdf_document.is_encrypted:
                pdf_document.close()
                raise ValueError(
                    "Password-protected PDFs are not supported."
                )

            page_count = pdf_document.page_count
            pdf_document.close()

            if page_count < 200:
                rejected_documents.append({
                    "filename": original_filename,
                    "pages": page_count,
                    "reason": "PDF must contain at least 200 pages."
                })
                continue

            with open(file_path, "wb") as pdf_file:
                pdf_file.write(content)

            document_metadata[safe_filename] = {
                "document_id": file_id,
                "original_filename": original_filename,
                "stored_filename": safe_filename,
                "page_count": page_count
            }

            uploaded_documents.append({
                "document_id": file_id,
                "filename": original_filename,
                "stored_filename": safe_filename,
                "page_count": page_count,
                "status": "uploaded"
            })

        except Exception as error:
            rejected_documents.append({
                "filename": original_filename,
                "reason": str(error)
            })

        finally:
            await file.close()

    # Save original filename information
    if uploaded_documents:
        metadata_path = os.path.join(
            session_dir,
            "metadata.json"
        )

        with open(metadata_path, "w", encoding="utf-8") as metadata_file:
            json.dump(
                document_metadata,
                metadata_file,
                ensure_ascii=False,
                indent=4
            )

    else:
        if os.path.exists(session_dir):
            os.rmdir(session_dir)

    return {
        "session_id": session_id if uploaded_documents else None,
        "total_files": len(files),
        "uploaded_count": len(uploaded_documents),
        "rejected_count": len(rejected_documents),
        "uploaded_documents": uploaded_documents,
        "rejected_documents": rejected_documents
    }
