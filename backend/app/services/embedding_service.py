import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

BACKEND_DIR = Path(__file__).resolve().parents[2]

CHUNKED_DIR = BACKEND_DIR / "storage" / "chunked"
EMBEDDING_DIR = BACKEND_DIR / "storage" / "embeddings"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 32

# Load the model once when this module is imported
model = SentenceTransformer(MODEL_NAME)


def generate_session_embeddings(session_id: str):

    input_dir = CHUNKED_DIR / session_id

    if not input_dir.exists():
        raise FileNotFoundError("Chunked documents not found")

    chunk_files = list(input_dir.glob("*_chunks.jsonl"))

    if not chunk_files:
        raise FileNotFoundError("No chunk files found")

    output_dir = EMBEDDING_DIR / session_id
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for chunk_file in chunk_files:

        records = []

        with open(chunk_file, "r", encoding="utf-8") as file:
            for line in file:
                records.append(json.loads(line))

        if not records:
            continue

        texts = [record["text"] for record in records]

        embeddings = model.encode(
            texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        vector_path = output_dir / f"{chunk_file.stem}.npy"
        metadata_path = output_dir / f"{chunk_file.stem}_metadata.jsonl"

        np.save(vector_path, embeddings)

        with open(metadata_path, "w", encoding="utf-8") as file:
            for record in records:
                file.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

        results.append({
            "source_file": chunk_file.name,
            "total_chunks": len(records),
            "embedding_dimensions": int(embeddings.shape[1]),
            "vector_file": str(vector_path),
            "metadata_file": str(metadata_path)
        })

    return results