
import json
import uuid
from pathlib import Path

from transformers import AutoTokenizer


# Project directories
BACKEND_DIR = Path(__file__).resolve().parents[2]

EXTRACTED_DIR = BACKEND_DIR / "storage" / "extracted"
CHUNKED_DIR = BACKEND_DIR / "storage" / "chunked"


# Embedding model tokenizer
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Token-based chunking configuration
CHUNK_SIZE = 700
CHUNK_OVERLAP = 140


# Load tokenizer once
tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)


def split_into_chunks(text):
    """
    Split text into token-based chunks.

    Target chunk size: 700 tokens
    Overlap: 140 tokens (20%)
    """

    text = text.strip()

    if not text:
        return []

    token_ids = tokenizer.encode(
        text,
        add_special_tokens=False
    )

    if not token_ids:
        return []

    chunks = []
    start = 0

    while start < len(token_ids):

        end = min(start + CHUNK_SIZE, len(token_ids))

        chunk_tokens = token_ids[start:end]

        chunk_text = tokenizer.decode(
            chunk_tokens,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        ).strip()

        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "token_count": len(chunk_tokens)
            })

        if end >= len(token_ids):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def generate_chunk_id(
    session_id,
    document_id,
    page_number,
    chunk_index,
    chunk_text
):
    """
    Generate a deterministic UUID-compatible chunk ID.

    UUID5 generates a valid UUID from the chunk metadata
    and content, making IDs reproducible.
    """

    unique_string = (
        f"{session_id}|{document_id}|"
        f"{page_number}|{chunk_index}|{chunk_text}"
    )

    return str(
        uuid.uuid5(uuid.NAMESPACE_URL, unique_string)
    )


def chunk_session_documents(session_id: str):

    input_dir = EXTRACTED_DIR / session_id

    if not input_dir.exists():
        raise FileNotFoundError(
            "Extracted documents not found"
        )

    jsonl_files = list(input_dir.glob("*.jsonl"))

    if not jsonl_files:
        raise FileNotFoundError(
            "No extracted JSONL files found"
        )

    output_dir = CHUNKED_DIR / session_id
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for input_file in jsonl_files:

        output_file = (
            output_dir / f"{input_file.stem}_chunks.jsonl"
        )

        total_chunks = 0
        total_tokens = 0

        with open(input_file, "r", encoding="utf-8") as source, \
             open(output_file, "w", encoding="utf-8") as destination:

            for line in source:

                page_record = json.loads(line)

                text = page_record.get("text", "")

                page_chunks = split_into_chunks(text)

                for chunk_index, chunk in enumerate(page_chunks):

                    chunk_text = chunk["text"]
                    token_count = chunk["token_count"]

                    document_id = page_record.get("document_id")
                    page_number = page_record["page_number"]

                    chunk_id = generate_chunk_id(
                        session_id,
                        document_id,
                        page_number,
                        chunk_index,
                        chunk_text
                    )

                    chunk_record = {
                        "chunk_id": chunk_id,
                        "session_id": session_id,
                        "filename": page_record["filename"],
                        "stored_filename": page_record.get(
                            "stored_filename"
                        ),
                        "document_id": document_id,
                        "page_number": page_number,
                        "chunk_index": chunk_index,
                        "token_count": token_count,
                        "text": chunk_text
                    }

                    destination.write(
                        json.dumps(
                            chunk_record,
                            ensure_ascii=False
                        ) + "\n"
                    )

                    total_chunks += 1
                    total_tokens += token_count

        results.append({
            "filename": input_file.name,
            "total_chunks": total_chunks,
            "total_tokens": total_tokens,
            "average_tokens_per_chunk": (
                round(total_tokens / total_chunks, 2)
                if total_chunks else 0
            ),
            "output_file": str(output_file)
        })

    return results
