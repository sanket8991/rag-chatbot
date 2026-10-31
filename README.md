# PDF RAG Chatbot
An AI-powered Retrieval-Augmented Generation (RAG) platform that enables users to upload large PDF collections, retrieve relevant information through semantic search, and receive accurate, context-grounded answers with document and page-level citations.

The application combines modern web technologies, open-source embedding models, vector search, OCR-based document processing, and Large Language Models to provide an interactive document intelligence experience.

---

## Overview

The PDF RAG Chatbot transforms large collections of PDF documents into a searchable knowledge base.

Users can upload documents, process their contents, and ask natural-language questions. The system retrieves relevant passages from the indexed documents and uses an LLM to generate answers supported by the retrieved context.

**Key capabilities:**
- Multiple PDF document uploads.
- Native PDF text extraction.
- OCR-based extraction for scanned pages.
- Metadata-preserving document chunking.
- Open-source semantic embedding generation.
- Vector indexing and similarity search.
- Context-grounded answer generation.
- PDF filename and page-level citations.
- Interactive React-based user interface.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, Vite |
| Backend | Python, FastAPI |
| PDF Processing | PyMuPDF |
| OCR | Tesseract OCR, pytesseract |
| Image Processing | Pillow |
| Embedding Model | Sentence Transformers — all-MiniLM-L6-v2 |
| Vector Database | Qdrant |
| LLM | OpenAI API |
| HTTP Client | Axios |
| Programming Languages | Python, JavaScript |

### Embedding Model

The project uses `sentence-transformers/all-MiniLM-L6-v2`, an open-source sentence embedding model that generates 384-dimensional vector representations.

### Vector Database

Qdrant provides persistent local vector storage and similarity search using cosine distance.

---

## System Architecture

The application follows a modular RAG architecture.

```text
                 USER
                  |
                  v
          REACT FRONTEND
                  |
                  v
             FASTAPI
                  |
                  v
          PDF DOCUMENT UPLOAD
                  |
                  v
          DOCUMENT PROCESSING
                  |
          +-------+--------+
          |                |
          v                v
    NATIVE EXTRACTION    OCR FALLBACK
       (PyMuPDF)         (Tesseract)
          |                |
          +-------+--------+
                  |
                  v
           TEXT PROCESSING
                  |
                  v
             CHUNKING
                  |
                  v
          EMBEDDING MODEL
          all-MiniLM-L6-v2
                  |
                  v
           QDRANT DATABASE
                  |
                  v
           SEMANTIC SEARCH
                  |
                  v
          RETRIEVED CONTEXT
                  |
                  v
            OPENAI LLM
                  |
                  v
          ANSWER GENERATION
                  |
                  v
        SOURCES AND CITATIONS
                  |
                  v
             USER
```

---

## Core Features

### 1. PDF Upload and Validation

- Upload multiple PDF documents through the web interface.
- Validate file types and PDF integrity.
- Validate minimum page-count requirements.
- Generate unique document and session identifiers.
- Preserve original document filenames and metadata.

### 2. Document Extraction and OCR

The system supports two extraction methods:

**Native PDF Text Extraction**
- Uses PyMuPDF to extract text directly from PDF pages.
- Preserves page-level information.

**OCR Fallback**
- Detects pages with insufficient native text.
- Renders pages as images.
- Uses Tesseract OCR to recognize text.
- Supports scanned PDF pages and image-based text.

Each extracted page records its extraction method, original filename, document ID and page number.

### 3. Text Chunking and Metadata

Extracted content is divided into smaller passages for efficient retrieval.

Each chunk maintains document metadata, including:

- Chunk ID.
- Session ID.
- Document ID.
- Original PDF filename.
- Stored filename.
- Page number.
- Chunk index.
- Extracted text.

This metadata enables source traceability during retrieval and answer generation.

### 4. Semantic Embedding Generation

The Sentence Transformers embedding model converts document chunks into numerical vector representations.

Model: `sentence-transformers/all-MiniLM-L6-v2`

Embedding dimension: 384

The generated embeddings are persisted for semantic search and retrieval.

### 5. Vector Indexing and Retrieval

Qdrant is used as the vector database.

Features include:
- Persistent local vector storage.
- Cosine similarity search.
- Session-based document filtering.
- Top-K relevant chunk retrieval.
- Relevance scores.
- Document and page metadata retrieval.

### 6. Retrieval-Augmented Answer Generation

When a user submits a question:

1. The question is converted into an embedding.
2. Qdrant searches for semantically relevant document chunks.
3. Retrieved passages are supplied as context to the LLM.
4. The LLM generates an answer grounded in the retrieved content.
5. The response includes source references.

The generation process is designed to reduce unsupported responses by grounding answers in retrieved document content.

### 7. Source Citations and Explainability

Answers include document provenance through:

- Original PDF filename.
- PDF page number.
- Retrieved source information.
- Relevance scores.

This allows users to trace generated answers back to the source documents.

---

## Frontend Interface

The React application provides three primary sections.

**Documents**
- Upload PDF documents.
- View upload results.
- Track document sessions.

**Processing**
- Run document extraction.
- Generate text chunks.
- Generate embeddings.
- Index vectors in Qdrant.
- View processing progress and status.

**Ask Questions**
- Enter natural-language questions.
- Retrieve relevant PDF passages.
- View generated answers.
- Inspect PDF source citations and relevance scores.

---

## Backend API

The FastAPI backend exposes the following endpoints.

| Endpoint | Method | Description |
|---|---|---|
| `/api/documents/upload` | POST | Upload and validate PDF documents |
| `/api/documents/{session_id}/extract` | POST | Extract text and perform OCR fallback |
| `/api/documents/{session_id}/chunk` | POST | Generate document chunks |
| `/api/documents/{session_id}/embed` | POST | Generate vector embeddings |
| `/api/documents/{session_id}/index` | POST | Index embeddings in Qdrant |
| `/api/documents/{session_id}/ask` | POST | Retrieve context and generate answers |

Interactive API documentation is available through FastAPI Swagger UI.

---

## Project Structure

```text
rag-chatbot/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── routes/
│   │   │   ├── upload.py
│   │   │   ├── process.py
│   │   │   ├── chunk.py
│   │   │   ├── embed.py
│   │   │   ├── indexing.py
│   │   │   ├── search.py
│   │   │   └── ask.py
│   │   │
│   │   └── services/
│   │       ├── pdf_extractor.py
│   │       ├── chunker.py
│   │       ├── embedding_service.py
│   │       ├── qdrant_service.py
│   │       ├── retrieval_service.py
│   │       └── llm_service.py
│   │
│   ├── uploads/
│   ├── storage/
│   ├── requirements.txt
│   └── .env.example
│
├── src/
│   ├── components/
│   │   ├── FileUpload.jsx
│   │   ├── Processing.jsx
│   │   └── AskQuestions.jsx
│   │
│   ├── services/
│   │   └── api.js
│   │
│   ├── App.jsx
│   └── App.css
│
├── public/
├── package.json
├── README.md
└── .gitignore
```

---

## Local Installation and Setup

### Prerequisites

- Python 3.10 or later.
- Node.js and npm.
- Git.
- Tesseract OCR.
- An OpenAI API key.

### 1. Clone the repository

```bash
git clone https://github.com/sanket8991/rag-chatbot.git
cd rag-chatbot
```

### 2. Set up the Python environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```powershell
pip install -r backend/requirements.txt
```

### 4. Install Tesseract OCR

Install Tesseract for Windows and configure its executable path in the PDF extraction service.

Default installation path:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 5. Configure environment variables

Create `backend/.env` using `backend/.env.example` as a reference.

Configure the required OpenAI API credentials and model settings.

Never commit API keys or other secrets to GitHub.

### 6. Start the backend

```powershell
cd backend
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

### 7. Start the frontend

Open another terminal from the project root:

```powershell
npm install
npm run dev
```

Open the Vite development URL displayed in the terminal.

---

## End-to-End Workflow

1. Upload PDF documents.
2. Validate and register uploaded documents.
3. Extract text using PyMuPDF.
4. Apply OCR fallback to pages with insufficient native text.
5. Generate document chunks with metadata.
6. Generate vector embeddings.
7. Store embeddings in Qdrant.
8. Submit a natural-language question.
9. Retrieve relevant document passages.
10. Generate an answer using retrieved context.
11. Display the answer with source citations.

---

## Performance and Evaluation

The system is designed around the following evaluation dimensions:

- Retrieval relevance.
- Recall@K.
- Mean Reciprocal Rank (MRR).
- Answer faithfulness.
- Hallucination rate.
- Citation accuracy.
- Average response latency.
- p95 response latency.
- Ingestion throughput.

Performance targets and evaluation results should be reported using measurements from the target dataset and hardware.

---

## Future Scalability

The architecture supports extension toward:

- Larger PDF collections.
- Advanced OCR preprocessing.
- Improved chunking strategies.
- Retrieval reranking.
- Retrieval visualization.
- Automated evaluation.
- Latency and throughput monitoring.
- Production deployment.

---

## Repository

GitHub: https://github.com/sanket8991/rag-chatbot

**Project:** PDF Retrieval-Augmented Generation Chatbot  
**Category:** AI / Machine Learning  
**Architecture:** React + FastAPI + Open-Source Embeddings + Qdrant + LLM
