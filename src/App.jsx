import { useState } from "react";
import FileUpload from "./components/FileUpload";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("documents");

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h2>PDF RAG</h2>
          <span>Document Intelligence Platform</span>
        </div>
        <div className="status">
          <span className="status-dot"></span>
          Local system
        </div>
      </header>

      <main className="dashboard">
        <section className="welcome">
          <div>
            <p className="eyebrow">RETRIEVAL AUGMENTED GENERATION</p>
            <h1>PDF Knowledge Assistant</h1>
            <p>
              Upload documents, process their contents, and ask questions across
              your PDF library.
            </p>
          </div>
        </section>

        <nav className="tabs">
          <button
            className={activeTab === "documents" ? "active" : ""}
            onClick={() => setActiveTab("documents")}
          >
            Documents
          </button>

          <button
            className={activeTab === "processing" ? "active" : ""}
            onClick={() => setActiveTab("processing")}
          >
            Processing
          </button>

          <button
            className={activeTab === "chat" ? "active" : ""}
            onClick={() => setActiveTab("chat")}
          >
            Ask Questions
          </button>
        </nav>

        {activeTab === "documents" && (
          <section className="panel">
            <h2>Upload PDF documents</h2>
            <p className="description">
              Upload multiple PDF files to create a searchable document
              collection.
            </p>
            <FileUpload />
          </section>
        )}

        {activeTab === "processing" && (
          <section className="panel">
            <h2>Document processing pipeline</h2>
            <p className="description">
              Track the progress of extraction, chunking, embedding generation,
              and indexing.
            </p>
            <p>
              Processing controls will be connected to the backend in the next
              step.
            </p>
          </section>
        )}

        {activeTab === "chat" && (
          <section className="panel">
            <h2>Ask your documents</h2>
            <p className="description">
              Ask questions and receive answers grounded in your uploaded PDFs.
            </p>
            <p>
              The chat interface and source citations will be connected next.
            </p>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
