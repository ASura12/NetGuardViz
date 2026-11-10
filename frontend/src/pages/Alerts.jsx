import { useEffect, useState } from "react";
import { getAlerts, deleteAlert, getUserRole } from "../services/api";
import { useNavigate } from "react-router-dom";
import "./Alerts.css";

// Alerts raised by the live capture agents (app/capture.py, app/wifi_capture.py)
// have a `type` and `severity`; keyword alerts from uploaded logs do not.
function formatTimestamp(ts) {
  if (!ts) return "N/A";
  // The backend stores naive UTC (datetime.utcnow().isoformat()), so mark it as UTC.
  const iso = /[zZ]|[+-]\d\d:\d\d$/.test(ts) ? ts : `${ts}Z`;
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? String(ts) : d.toLocaleString();
}

function SiemAlertCard({ alert, isAdmin, onDelete }) {
  const severity = String(alert.severity || "LOW").toUpperCase();
  const isWifi = alert.source === "wifi";
  const sourceId = alert.src_ip || alert.src_mac;
  return (
    <article className={`alert-card siem-card sev-${severity.toLowerCase()}`}>
      <div className="row">
        <h3>{String(alert.type).replace(/_/g, " ")}</h3>
        <span className={`badge sev-badge sev-${severity.toLowerCase()}`}>{severity}</span>
      </div>

      <p className="meta">Source: <strong>{isWifi ? "Wi-Fi (802.11)" : "Network"}</strong></p>
      <p className="meta">Detected: <strong>{formatTimestamp(alert.timestamp)}</strong></p>
      {sourceId && (
        <p className="meta">
          {alert.src_ip ? "Source IP" : "MAC / BSSID"}: <strong>{String(sourceId)}</strong>
        </p>
      )}
      {alert.detail && <p className="meta siem-detail">{alert.detail}</p>}

      {isAdmin && (
        <div style={{ marginTop: 12 }}>
          <button className="btn btn-danger" onClick={() => onDelete(alert._id || alert.id)}>
            Delete
          </button>
        </div>
      )}
    </article>
  );
}

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);
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

  useEffect(() => {
    const role = getUserRole();
    setIsAdmin(role === "admin");
  }, []);

  const handleDelete = async (alertId) => {
    if (!alertId) return;
    const ok = window.confirm("Delete this alert permanently? This action cannot be undone.");
    if (!ok) return;
    try {
      await deleteAlert(alertId);
      await fetchAlerts();
    } catch (e) {
      setError(e?.message || "Delete failed");
    }
  };

  return (
    <div className="alerts-page">
      <header className="alerts-header">
        <div>
          <p className="eyebrow">NetGuardViz Response Feed</p>
          <h2>Suspicious Alerts</h2>
          <p className="subtext">Suspicious keywords found in uploaded logs, plus live detections from the network and Wi-Fi capture agents.</p>
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
          {alerts.map((alert, idx) => alert.type ? (
            <SiemAlertCard
              key={`${alert.id || alert._id || "siem"}-${idx}`}
              alert={alert}
              isAdmin={isAdmin}
              onDelete={handleDelete}
            />
          ) : (
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
              {isAdmin && (
                <div style={{ marginTop: 12 }}>
                  <button className="btn btn-danger" onClick={() => handleDelete(alert._id || alert.id || alert.log_id)}>
                    Delete
                  </button>
                </div>
              )}
            </article>
          ))}
        </section>
      )}
    </div>
  );
}