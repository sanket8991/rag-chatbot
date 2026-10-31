from app.services.embedding_service import model
from app.services.qdrant_service import client, COLLECTION_NAME
from qdrant_client import models


def search_session_documents(
    session_id: str,
    question: str,
    top_k: int = 5
):
    # Convert the question into a vector
    query_vector = model.encode(
        question,
        normalize_embeddings=True,
        convert_to_numpy=True
    ).tolist()

    # Search only within this upload session
    search_results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="session_id",
                    match=models.MatchValue(value=session_id)
                )
            ]
        ),
        limit=top_k,
        with_payload=True
    )

    results = []

    for point in search_results.points:
        payload = point.payload or {}

        results.append({
            "score": point.score,
            "filename": payload.get("filename"),
            "stored_filename": payload.get("stored_filename"),
            "document_id": payload.get("document_id"),
            "page_number": payload.get("page_number"),
            "chunk_index": payload.get("chunk_index"),
            "text": payload.get("text")
        })

    return results