import { useState } from "react";
import api from "../services/api";
import "./AskQuestions.css";

function AskQuestions({ sessionId }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAsk = async (event) => {
    event.preventDefault();

    if (!sessionId) {
      setError("Please upload and process your PDFs first.");
      return;
    }

    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);

    try {
      const response = await api.post(`/api/documents/${sessionId}/ask`, {
        question: question.trim(),
        top_k: 5,
      });

      setAnswer(response.data.answer || "No answer was generated.");
      setSources(response.data.sources || []);
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        "Something went wrong while answering your question.";

      setError(typeof message === "string" ? message : JSON.stringify(message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ask-container">
      <div className="ask-header">
        <h2>Ask your documents</h2>
        <p>
          Ask questions and receive answers based on your uploaded PDF
          documents.
        </p>
      </div>

      {!sessionId && (
        <div className="ask-notice">
          Upload and process your PDFs before asking questions.
        </div>
      )}

      <form onSubmit={handleAsk} className="ask-form">
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="For example: What are the main findings in these documents?"
          rows={4}
          disabled={loading || !sessionId}
        />

        <button
          type="submit"
          disabled={loading || !sessionId || !question.trim()}
        >
          {loading ? "Searching documents..." : "Ask Question"}
        </button>
      </form>

      {loading && (
        <div className="ask-loading">
          Searching your documents and generating an answer...
        </div>
      )}

      {error && (
        <div className="ask-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {answer && (
        <div className="answer-section">
          <h3>Answer</h3>
          <div className="answer-content">{answer}</div>
        </div>
      )}

      {sources.length > 0 && (
        <div className="sources-section">
          <h3>Sources</h3>

          {sources.map((source, index) => (
            <div
              className="source-card"
              key={`${source.document_id || source.filename}-${source.page_number}-${index}`}
            >
              <div className="source-title">
                {source.filename || "Unknown document"}
              </div>

              <div className="source-details">
                PDF page: {source.page_number ?? "N/A"}
              </div>

              {typeof source.relevance_score === "number" && (
                <div className="source-details">
                  Relevance score: {source.relevance_score.toFixed(4)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AskQuestions;
