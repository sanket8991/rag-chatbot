
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.upload import router as upload_router
from app.routes.process import router as process_router
from app.routes.chunk import router as chunk_router
from app.routes.embed import router as embed_router
from app.routes.indexing import router as indexing_router
from app.routes.search import router as search_router
from app.routes.ask import router as ask_router

app = FastAPI(
    title="RAG PDF Chatbot API",
    description="Backend API for our PDF-based RAG chatbot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    upload_router,
    prefix="/api/documents",
    tags=["Documents"]
)

app.include_router(
    process_router,
    prefix="/api/documents",
    tags=["Documents"]
)

app.include_router(
    chunk_router,
    prefix="/api/documents",
    tags=["Documents"]
)

app.include_router(
    embed_router,
    prefix="/api/documents",
    tags=["Documents"]
)

app.include_router(
    indexing_router,
    prefix="/api/documents",
    tags=["Documents"]
)

app.include_router(
    search_router,
    prefix="/api/documents",
    tags=["Documents"]
)

app.include_router(
    ask_router,
    prefix="/api/documents",
    tags=["Documents"]
)

@app.get("/")
def home():
    return {"message": "RAG Chatbot API is running!"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "RAG Backend"
    }

@app.get("/api/test")
def test_api():
    return {
        "success": True,
        "message": "React and FastAPI can communicate!"
    }
