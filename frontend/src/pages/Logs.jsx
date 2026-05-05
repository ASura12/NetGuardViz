import { useEffect, useState } from "react";
import { getLogs, uploadLog, deleteLog } from "../services/api";
import { useNavigate } from "react-router-dom";
import "./Logs.css";

export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState(null);
  const navigate = useNavigate();

  const fetchLogs = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/");
        return;
      }

      const response = await getLogs();
      if (response?.detail) {
        if (String(response.detail).toLowerCase().includes("not authenticated")) {
          localStorage.removeItem("token");
          navigate("/");
          return;
        }
        setError(String(response.detail));
        return;
      }

      setLogs(Array.isArray(response?.data) ? response.data : []);
      setError("");
    } catch (err) {
      setError("Unable to load logs.");
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [navigate]);

  const handleUpload = async () => {
    if (!file) {
      setError("Please choose a .log, .txt, or .json file before uploading.");
      return;
    }

    try {
      setUploading(true);
      setError("");
      await uploadLog(file);
      setFile(null);
      await fetchLogs();
    } catch (err) {
      setError(err?.message || "Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (logId) => {
    const ok = window.confirm("Delete this log permanently? This action cannot be undone.");
    if (!ok) return;
    try {
      setError("");
      await deleteLog(logId);
      await fetchLogs();
    } catch (err) {
      setError(err?.message || "Delete failed.");
    }
  };

  return (
    <div className="logs-page">
      <header className="logs-header">
        <div>
          <p className="eyebrow">NetGuardViz Intake</p>
          <h2>Log Upload and Review</h2>
          <p className="subtext">Upload security logs and review ingestion status in one place.</p>
        </div>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={() => navigate("/dashboard")}>Dashboard</button>
          <button className="btn btn-secondary" onClick={() => navigate("/alerts")}>Alerts</button>
        </div>
      </header>

      <section className="upload-card">
        <input
          id="log-upload"
          className="file-input"
          type="file"
          accept=".log,.txt,.json"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <button className="btn btn-primary" onClick={handleUpload} disabled={uploading}>
          {uploading ? "Uploading..." : "Upload Log"}
        </button>
      </section>

      {error && <p className="error-banner">{error}</p>}

      {logs.length === 0 ? (
        <p className="empty-state">No logs available yet. Upload a file to start analysis.</p>
      ) : (
        <section className="logs-grid">
          {logs.map((log, idx) => (
            <article className="log-card" key={log.id || `${log.filename || "log"}-${idx}`}>
              <div className="row">
                <h3>{log.filename || "Unnamed Log"}</h3>
                <span className={`badge ${log.suspicious ? "badge-alert" : "badge-safe"}`}>
                  {log.suspicious ? "Suspicious" : "Clean"}
                </span>
              </div>

              <p className="meta">Status: <strong>{log.status || "pending"}</strong></p>
              <p className="preview">{String(log.content || "").slice(0, 180) || "No content preview available."}</p>
              
              <div style={{ marginTop: 12 }}>
                <button className="btn btn-danger" onClick={() => handleDelete(log.id)}>
                  Delete
                </button>
              </div>
            </article>
          ))}
        </section>
      )}
    </div>
  );
}