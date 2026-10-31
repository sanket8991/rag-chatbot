import json
import uuid
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]

EXTRACTED_DIR = BACKEND_DIR / "storage" / "extracted"
CHUNKED_DIR = BACKEND_DIR / "storage" / "chunked"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def split_into_chunks(text):
    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))

        # Prefer ending at a word boundary
        if end < len(text):
            space_position = text.rfind(" ", start, end)

            if space_position > start + int(CHUNK_SIZE * 0.7):
                end = space_position

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(end - CHUNK_OVERLAP, start + 1)

    return chunks


def chunk_session_documents(session_id: str):

    input_dir = EXTRACTED_DIR / session_id

    if not input_dir.exists():
        raise FileNotFoundError("Extracted documents not found")

    jsonl_files = list(input_dir.glob("*.jsonl"))

    if not jsonl_files:
        raise FileNotFoundError("No extracted JSONL files found")

    output_dir = CHUNKED_DIR / session_id
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for input_file in jsonl_files:

        output_file = output_dir / f"{input_file.stem}_chunks.jsonl"

        total_chunks = 0

        with open(input_file, "r", encoding="utf-8") as source, \
             open(output_file, "w", encoding="utf-8") as destination:

            for line in source:

                page_record = json.loads(line)

                text = page_record["text"]
                page_chunks = split_into_chunks(text)

                for chunk_index, chunk_text in enumerate(page_chunks):

                    chunk_record = {
                        "chunk_id": str(uuid.uuid4()),
                        "session_id": session_id,
                        "filename": page_record["filename"],
                        "stored_filename": page_record.get("stored_filename"),
                        "document_id": page_record.get("document_id"),
                        "page_number": page_record["page_number"],
                        "chunk_index": chunk_index,
                        "text": chunk_text
                    }

                    destination.write(
                        json.dumps(chunk_record, ensure_ascii=False) + "\n"
                    )

                    total_chunks += 1

        results.append({
            "filename": input_file.name,
            "total_chunks": total_chunks,
            "output_file": str(output_file)
        })

    return results