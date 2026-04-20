import { useEffect, useState } from "react";
import { getLogs, getStats } from "../services/api";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

export default function Dashboard() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({ total_logs: 0, total_alerts: 0, suspicious_percentage: 0 });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          navigate("/");
          return;
        }

        const [logsData, statsData] = await Promise.all([getLogs(), getStats()]);
        setLogs(Array.isArray(logsData?.data) ? logsData.data : []);
        setStats({
          total_logs: Number(statsData?.total_logs || 0),
          total_alerts: Number(statsData?.total_alerts || 0),
          suspicious_percentage: Number(statsData?.suspicious_percentage || 0),
        });
      } catch (err) {
        const message = String(err?.message || "Server error").toLowerCase();
        if (message.includes("not authenticated")) {
          localStorage.removeItem("token");
          navigate("/");
          return;
        }
        setError(err?.message || "Server error");
      }
    };

    fetchLogs();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  const processedCount = logs.filter((log) => String(log?.status || "").toLowerCase() === "processed").length;

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">NetGuardViz Security Center</p>
          <h1>Threat Monitoring Dashboard</h1>
          <p className="subtext">Live overview of uploaded logs and suspicious activity signals.</p>
        </div>

        <div className="header-actions">
          <button className="btn btn-secondary" onClick={() => navigate("/logs")}>View Logs</button>
          <button className="btn btn-secondary" onClick={() => navigate("/alerts")}>View Alerts</button>
          <button className="btn btn-danger" onClick={handleLogout}>Logout</button>
        </div>
      </header>

      {error && <p className="error-banner">{error}</p>}

      <section className="stats-grid">
        <article className="stat-card">
          <p>Total Logs</p>
          <h2>{stats.total_logs}</h2>
        </article>
        <article className="stat-card">
          <p>Suspicious Logs</p>
          <h2>{stats.total_alerts}</h2>
        </article>
        <article className="stat-card">
          <p>Suspicious Rate</p>
          <h2>{stats.suspicious_percentage}%</h2>
        </article>
        <article className="stat-card">
          <p>Processed Logs (Current Page)</p>
          <h2>{processedCount}</h2>
        </article>
      </section>

      <section className="log-section">
        <div className="section-head">
          <h3>Recent Log Activity</h3>
        </div>

        {logs.length === 0 ? (
          <p className="empty-state">No logs found yet. Upload a file from the Logs page to start monitoring.</p>
        ) : (
          <div className="log-grid">
            {logs.map((log, i) => (
              <article key={log.id || i} className="log-card">
                <div className="log-top">
                  <h4>{log.filename || "Unnamed Log"}</h4>
                  <span className={`badge ${log.suspicious ? "badge-alert" : "badge-safe"}`}>
                    {log.suspicious ? "Suspicious" : "Clean"}
                  </span>
                </div>

                <p className="meta">
                  Status: <strong>{log.status || "pending"}</strong>
                </p>

                <p className="preview">{String(log.content || "").slice(0, 140) || "No content preview available."}</p>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}