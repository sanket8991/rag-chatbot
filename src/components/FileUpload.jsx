import { useState } from "react";
import api from "../services/api";
import "./FileUpload.css";

function FileUpload() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const handleFileChange = (event) => {
    const selectedFiles = Array.from(event.target.files || []);

    setFiles(selectedFiles);
    setResult(null);
    setError("");
    setCopied(false);
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setError("Please select PDF files first.");
      return;
    }

    const formData = new FormData();

    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      setLoading(true);
      setError("");
      setResult(null);

      const response = await api.post("/api/documents/upload", formData);

      setResult(response.data);
      setFiles([]);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Upload failed. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  const copySessionId = async () => {
    if (!result?.session_id) return;

    try {
      await navigator.clipboard.writeText(result.session_id);
      setCopied(true);
    } catch {
      setError("Could not copy the session ID.");
    }
  };

  const formatSize = (bytes) => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="upload-container">
      <div className="upload-header">
        <div>
          <h2>Upload PDF documents</h2>
          <p>Add your PDF files to create a searchable knowledge base.</p>
        </div>
        <div className="upload-icon">PDF</div>
      </div>

      <label className="drop-area">
        <div className="upload-symbol">↑</div>
        <strong>Select PDF documents</strong>
        <span>Choose one or multiple PDF files</span>
        <span className="browse-text">Browse files</span>

        <input
          type="file"
          accept=".pdf,application/pdf"
          multiple
          onChange={handleFileChange}
          disabled={loading}
        />
      </label>

      {files.length > 0 && (
        <div className="selected-section">
          <div className="section-heading">
            <h3>Selected files</h3>
            <span>{files.length} file(s)</span>
          </div>

          {files.map((file, index) => (
            <div className="file-row" key={`${file.name}-${index}`}>
              <div className="file-type">PDF</div>
              <div className="file-details">
                <strong>{file.name}</strong>
                <span>{formatSize(file.size)}</span>
              </div>
            </div>
          ))}

          <button
            className="upload-button"
            onClick={handleUpload}
            disabled={loading}
          >
            {loading ? "Uploading documents..." : "Upload documents"}
          </button>
        </div>
      )}

      {loading && (
        <div className="loading-message">
          Uploading and validating PDF documents. Please wait.
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      {result && (
        <div className="result-section">
          <div className="success-heading">
            <span className="success-icon">✓</span>
            <div>
              <h3>Upload completed</h3>
              <p>Your upload results are ready.</p>
            </div>
          </div>

          <div className="result-stats">
            <div className="stat-card">
              <strong>{result.uploaded_count ?? 0}</strong>
              <span>Uploaded</span>
            </div>

            <div className="stat-card">
              <strong>{result.rejected_count ?? 0}</strong>
              <span>Rejected</span>
            </div>
          </div>

          {result.session_id && (
            <div className="session-box">
              <span>UPLOAD SESSION ID</span>
              <div>
                <code>{result.session_id}</code>
                <button onClick={copySessionId}>
                  {copied ? "Copied" : "Copy"}
                </button>
              </div>
            </div>
          )}

          {result.uploaded_documents?.length > 0 && (
            <div className="document-list">
              <h3>Uploaded documents</h3>

              {result.uploaded_documents.map((doc) => (
                <div className="document-row" key={doc.document_id}>
                  <div className="document-icon">PDF</div>
                  <div className="document-details">
                    <strong>{doc.filename}</strong>
                    <span>{doc.page_count} pages</span>
                  </div>
                  <span className="document-status">Uploaded</span>
                </div>
              ))}
            </div>
          )}

          {result.rejected_documents?.length > 0 && (
            <div className="rejected-list">
              <h3>Rejected documents</h3>

              {result.rejected_documents.map((doc, index) => (
                <div key={`${doc.filename}-${index}`}>
                  <strong>{doc.filename}</strong>
                  <p>{doc.reason}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default FileUpload;
