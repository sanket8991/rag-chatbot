
import json
from pathlib import Path
import fitz

BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BACKEND_DIR / "uploads"
OUTPUT_DIR = BACKEND_DIR / "storage" / "extracted"


def extract_session_pdfs(session_id: str):
    session_dir = UPLOAD_DIR / session_id

    if not session_dir.exists():
        raise FileNotFoundError("Upload session not found")

    pdf_files = list(session_dir.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError("No PDF files found in this session")

    # Load original document metadata
    metadata_path = session_dir / "metadata.json"
    document_metadata = {}

    if metadata_path.exists():
        with open(metadata_path, "r", encoding="utf-8") as file:
            document_metadata = json.load(file)

    output_session_dir = OUTPUT_DIR / session_id
    output_session_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for pdf_path in pdf_files:

        file_metadata = document_metadata.get(pdf_path.name, {})

        original_filename = file_metadata.get(
            "original_filename",
            pdf_path.name
        )

        document_id = file_metadata.get("document_id")

        output_path = output_session_dir / f"{pdf_path.stem}.jsonl"

        total_chars = 0
        empty_pages = 0

        with fitz.open(pdf_path) as pdf:
            total_pages = len(pdf)

            with open(output_path, "w", encoding="utf-8") as output_file:

                for page_index, page in enumerate(pdf):

                    text = page.get_text("text").strip()

                    if not text:
                        empty_pages += 1

                    total_chars += len(text)

                    record = {
                        "filename": original_filename,
                        "stored_filename": pdf_path.name,
                        "document_id": document_id,
                        "page_number": page_index + 1,
                        "text": text,
                    }

                    output_file.write(
                        json.dumps(record, ensure_ascii=False) + "\n"
                    )

        results.append({
            "filename": original_filename,
            "stored_filename": pdf_path.name,
            "document_id": document_id,
            "total_pages": total_pages,
            "total_characters": total_chars,
            "empty_pages": empty_pages,
            "output_file": str(output_path),
        })

    return results
