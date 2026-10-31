import { useState } from "react";
import FileUpload from "./components/FileUpload";
import Processing from "./components/Processing";
import AskQuestions from "./components/AskQuestions";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("documents");
  const [sessionId, setSessionId] = useState("");

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
            <FileUpload onUploadSuccess={setSessionId} />
          </section>
        )}

        {activeTab === "processing" && (
          <section className="panel">
            <Processing sessionId={sessionId} />
          </section>
        )}

        {activeTab === "chat" && (
          <section className="panel">
            <AskQuestions sessionId={sessionId} />
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
