import { useEffect, useState } from "react";
import { getAlerts } from "../services/api";
import { useNavigate } from "react-router-dom";
import "./Alerts.css";

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const fetchAlerts = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/");
        return;
      }

      const response = await getAlerts();
      if (response?.detail) {
        if (String(response.detail).toLowerCase().includes("not authenticated")) {
          localStorage.removeItem("token");
          navigate("/");
          return;
        }
        setError(String(response.detail));
        return;
      }

      setAlerts(Array.isArray(response?.data) ? response.data : []);
      setError("");
    } catch (err) {
      setError("Unable to load alerts.");
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [navigate]);

  return (
    <div className="alerts-page">
      <header className="alerts-header">
        <div>
          <p className="eyebrow">NetGuardViz Response Feed</p>
          <h2>Suspicious Alerts</h2>
          <p className="subtext">Events generated from suspicious keyword detection in uploaded logs.</p>
        </div>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={() => navigate("/dashboard")}>Dashboard</button>
          <button className="btn btn-secondary" onClick={() => navigate("/logs")}>Logs</button>
        </div>
      </header>

      {error && <p className="error-banner">{error}</p>}

      {alerts.length === 0 ? (
        <p className="empty-state">No alerts found. Upload logs and wait for analysis to complete.</p>
      ) : (
        <section className="alerts-grid">
          {alerts.map((alert, idx) => (
            <article className="alert-card" key={`${alert.log_id || "alert"}-${idx}`}>
              <div className="row">
                <h3>Alert #{idx + 1}</h3>
                <span className="badge">Suspicious</span>
              </div>

              <p className="meta">Log ID: <strong>{String(alert.log_id || "N/A")}</strong></p>
              <p className="meta">Created: <strong>{alert.created_at ? new Date(alert.created_at).toLocaleString() : "N/A"}</strong></p>

              <p className="meta keywords-label">Detected Keywords</p>
              <div className="keyword-wrap">
                {(Array.isArray(alert.detected_keywords) ? alert.detected_keywords : []).length === 0 ? (
                  <span className="keyword-pill keyword-empty">None</span>
                ) : (
                  (alert.detected_keywords || []).map((kw, kwIdx) => (
                    <span className="keyword-pill" key={`${kw}-${kwIdx}`}>{kw}</span>
                  ))
                )}
              </div>
            </article>
          ))}
        </section>
      )}
    </div>
  );
}