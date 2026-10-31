import { useState } from "react";
import api from "../services/api";
import "./Processing.css";

const stages = [
  {
    id: "extract",
    title: "Extract PDF text",
    description: "Extract text and page information from uploaded PDFs.",
    endpoint: "extract",
  },
  {
    id: "chunk",
    title: "Chunk documents",
    description: "Split extracted text into overlapping text chunks.",
    endpoint: "chunk",
  },
  {
    id: "embed",
    title: "Generate embeddings",
    description: "Convert text chunks into 384-dimensional vectors.",
    endpoint: "embed",
  },
  {
    id: "index",
    title: "Index in Qdrant",
    description: "Store vectors and document metadata for retrieval.",
    endpoint: "index",
  },
];

function Processing({ sessionId }) {
  const [statuses, setStatuses] = useState({});
  const [results, setResults] = useState({});
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [completed, setCompleted] = useState(false);

  const updateStatus = (stage, status) => {
    setStatuses((previous) => ({
      ...previous,
      [stage]: status,
    }));
  };

  const runPipeline = async () => {
    if (!sessionId) {
      setError({
        stage: "Upload",
        message: "Please upload PDF documents before processing.",
        statusCode: null,
      });
      return;
    }

    setRunning(true);
    setError(null);
    setCompleted(false);
    setStatuses({});
    setResults({});

    for (const stage of stages) {
      updateStatus(stage.id, "running");

      try {
        const response = await api.post(
          `/api/documents/${sessionId}/${stage.endpoint}`,
        );

        setResults((previous) => ({
          ...previous,
          [stage.id]: response.data,
        }));

        updateStatus(stage.id, "success");
      } catch (err) {
        updateStatus(stage.id, "failed");

        const statusCode = err.response?.status;
        const backendDetail = err.response?.data?.detail;

        let errorMessage = "An unexpected error occurred.";

        if (backendDetail) {
          errorMessage =
            typeof backendDetail === "string"
              ? backendDetail
              : JSON.stringify(backendDetail);
        } else if (err.code === "ECONNABORTED") {
          errorMessage = "Request timed out. The operation may need more time.";
        } else if (err.message === "Network Error") {
          errorMessage =
            "Cannot connect to the backend. Check whether FastAPI is running.";
        } else if (err.message) {
          errorMessage = err.message;
        }

        setError({
          stage: stage.title,
          message: errorMessage,
          statusCode: statusCode || null,
        });

        setRunning(false);
        return;
      }
    }

    setCompleted(true);
    setRunning(false);
  };

  const getStatusLabel = (status) => {
    if (status === "success") return "Completed";
    if (status === "running") return "Running...";
    if (status === "failed") return "Failed";
    return "Pending";
  };

  const getCount = (stageId) => {
    const data = results[stageId];

    if (!data) return null;

    if (stageId === "extract") {
      return data.documents?.reduce(
        (sum, doc) => sum + (doc.total_pages || 0),
        0,
      );
    }

    if (stageId === "chunk") {
      return data.documents?.reduce(
        (sum, doc) => sum + (doc.total_chunks || 0),
        0,
      );
    }

    if (stageId === "embed") {
      return data.documents?.reduce(
        (sum, doc) => sum + (doc.total_vectors || 0),
        0,
      );
    }

    if (stageId === "index") {
      return data.total_indexed ?? 0;
    }

    return null;
  };

  const getCountLabel = (stageId) => {
    const labels = {
      extract: "pages extracted",
      chunk: "chunks generated",
      embed: "vectors generated",
      index: "vectors indexed",
    };

    return labels[stageId] || "";
  };

  return (
    <div className="processing-container">
      <div className="processing-header">
        <div>
          <h2>Document processing pipeline</h2>
          <p>Process uploaded PDFs and prepare them for semantic search.</p>
        </div>
      </div>

      {sessionId ? (
        <div className="processing-session">
          <span>ACTIVE SESSION</span>
          <code>{sessionId}</code>
        </div>
      ) : (
        <div className="processing-warning">
          No upload session found. Upload your PDFs in the Documents tab first.
        </div>
      )}

      <div className="pipeline-list">
        {stages.map((stage, index) => {
          const status = statuses[stage.id] || "pending";
          const count = getCount(stage.id);

          return (
            <div className="pipeline-stage" key={stage.id}>
              <div className={`stage-number ${status}`}>
                {status === "success" ? "✓" : index + 1}
              </div>

              <div className="stage-content">
                <div className="stage-title-row">
                  <h3>{stage.title}</h3>

                  <span className={`stage-status ${status}`}>
                    {getStatusLabel(status)}
                  </span>
                </div>

                <p>{stage.description}</p>

                {count !== null && (
                  <span className="stage-result">
                    {count.toLocaleString()} {getCountLabel(stage.id)}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {error && (
        <div className="processing-error">
          <strong>Processing failed</strong>

          <p>
            <b>Failed stage:</b> {error.stage}
          </p>

          <p>
            <b>Reason:</b> {error.message}
          </p>

          {error.statusCode && (
            <p>
              <b>HTTP status:</b> {error.statusCode}
            </p>
          )}

          <span>Fix the issue and run the pipeline again.</span>
        </div>
      )}

      {completed && (
        <div className="processing-success">
          <strong>Processing completed successfully!</strong>
          <p>
            Your documents are now indexed in Qdrant and ready for retrieval.
          </p>
        </div>
      )}

      <button
        className="run-pipeline-button"
        onClick={runPipeline}
        disabled={!sessionId || running}
      >
        {running
          ? "Processing documents..."
          : completed
            ? "Run pipeline again"
            : "Run processing pipeline"}
      </button>
    </div>
  );
}

export default Processing;
