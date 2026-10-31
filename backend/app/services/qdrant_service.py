import json
from pathlib import Path

import numpy as np
from qdrant_client import QdrantClient, models

BACKEND_DIR = Path(__file__).resolve().parents[2]

EMBEDDING_DIR = BACKEND_DIR / "storage" / "embeddings"
QDRANT_PATH = BACKEND_DIR / "storage" / "qdrant"

COLLECTION_NAME = "pdf_chunks"
VECTOR_SIZE = 384
BATCH_SIZE = 100

QDRANT_PATH.mkdir(parents=True, exist_ok=True)

# One persistent local Qdrant client for this application process
client = QdrantClient(path=str(QDRANT_PATH))


def index_session_embeddings(session_id: str):

    input_dir = EMBEDDING_DIR / session_id

    if not input_dir.exists():
        raise FileNotFoundError("Embeddings not found for this session")

    vector_files = list(input_dir.glob("*.npy"))

    if not vector_files:
        raise FileNotFoundError("No vector files found")

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE
            )
        )

    total_indexed = 0
    results = []

    for vector_file in vector_files:

        metadata_file = input_dir / (
            f"{vector_file.stem}_metadata.jsonl"
        )

        if not metadata_file.exists():
            raise FileNotFoundError(
                f"Metadata file not found: {metadata_file.name}"
            )

        vectors = np.load(vector_file)

        with open(metadata_file, "r", encoding="utf-8") as file:
            records = [
                json.loads(line)
                for line in file
            ]

        if len(vectors) != len(records):
            raise ValueError(
                "Vector count does not match metadata count"
            )

        if vectors.ndim != 2 or vectors.shape[1] != VECTOR_SIZE:
            raise ValueError("Unexpected embedding dimensions")

        for start in range(0, len(records), BATCH_SIZE):

            end = min(start + BATCH_SIZE, len(records))

            points = []

            for index in range(start, end):

                record = records[index]

                points.append(
                    models.PointStruct(
                        id=record["chunk_id"],
                        vector=vectors[index].tolist(),
                        payload={
                            "session_id": session_id,
                            "filename": record["filename"],
                            "stored_filename": record.get("stored_filename"),
                            "document_id": record.get("document_id"),
                            "page_number": record["page_number"],
                            "chunk_index": record["chunk_index"],
                            "text": record["text"]
                        }
                    )
                )

            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
                wait=True
            )

            total_indexed += len(points)

        results.append({
            "source_file": vector_file.name,
            "total_vectors": len(vectors)
        })

    return {
        "total_indexed": total_indexed,
        "documents": results
    }