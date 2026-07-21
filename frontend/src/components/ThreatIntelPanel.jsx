import { useEffect, useState, useCallback } from "react";

/**
 * ThreatIntelPanel
 *
 * Displays the SIEM alert summary (severity counts + recent alerts)
 * pulled from GET /api/threats/summary.
 *
 * Usage:
 *   <ThreatIntelPanel token={eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhc2h1dG9zaEBnbWFpbC5jb20iLCJyb2xlIjoidXNlciIsImV4cCI6MTc4NDU2ODM0NH0.Iw8N9OnuR6kJNsSI1Br_YPtBHxol8XT1rxQSCD7F-LU} />
 *
 * `token` is the JWT access_token returned from your /auth/login endpoint.
 * Store it in your app's auth context / state after login and pass it down.
 */

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const SEVERITY_STYLES = {
  CRITICAL: { bg: "#fcebeb", border: "#f09595", text: "#791f1f" },
  HIGH: { bg: "#faeeda", border: "#ef9f27", text: "#633806" },
  MEDIUM: { bg: "#e6f1fb", border: "#85b7eb", text: "#0c447c" },
  LOW: { bg: "#f1efe8", border: "#b4b2a9", text: "#444441" },
};

function SeverityBadge({ level }) {
  const style = SEVERITY_STYLES[level] || SEVERITY_STYLES.LOW;
  return (
    <span
      style={{
        background: style.bg,
        color: style.text,
        border: `1px solid ${style.border}`,
        borderRadius: 6,
        padding: "2px 10px",
        fontSize: 12,
        fontWeight: 500,
        whiteSpace: "nowrap",
      }}
    >
      {level}
    </span>
  );
}

function StatCard({ label, value, level }) {
  const style = SEVERITY_STYLES[level] || SEVERITY_STYLES.LOW;
  return (
    <div
      style={{
        flex: 1,
        minWidth: 100,
        background: "#fff",
        border: `1px solid ${style.border}`,
        borderRadius: 10,
        padding: "12px 16px",
      }}
    >
      <div style={{ fontSize: 12, color: "#6b6b6b", marginBottom: 4 }}>
        {label}
      </div>
      <div style={{ fontSize: 24, fontWeight: 600, color: style.text }}>
        {value}
      </div>
    </div>
  );
}

export default function ThreatIntelPanel({ token }) {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchSummary = useCallback(async () => {
    if (!token) {
      setError("Not authenticated. Please log in.");
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/threats/summary`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.status === 401) {
        setError("Session expired or unauthorized. Please log in again.");
        setSummary(null);
        return;
      }
      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`);
      }

      const data = await res.json();
      setSummary(data);
      setError(null);
    } catch (err) {
      setError(err.message || "Failed to load threat intel summary.");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchSummary();
    const interval = setInterval(fetchSummary, 15000); // refresh every 15s
    return () => clearInterval(interval);
  }, [fetchSummary]);

  return (
    <div
      style={{
        background: "#fafafa",
        border: "1px solid #e0e0e0",
        borderRadius: 12,
        padding: 20,
        fontFamily: "sans-serif",
        maxWidth: 720,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>
          Threat Intelligence Summary
        </h3>
        <button
          onClick={fetchSummary}
          style={{
            fontSize: 12,
            padding: "4px 10px",
            border: "1px solid #ccc",
            borderRadius: 6,
            background: "#fff",
            cursor: "pointer",
          }}
        >
          Refresh
        </button>
      </div>

      {loading && !summary && (
        <p style={{ fontSize: 13, color: "#888" }}>Loading alerts…</p>
      )}

      {error && (
        <p style={{ fontSize: 13, color: "#791f1f" }}>{error}</p>
      )}

      {summary && (
        <>
          <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
            <StatCard label="Critical" value={summary.summary?.CRITICAL ?? 0} level="CRITICAL" />
            <StatCard label="High" value={summary.summary?.HIGH ?? 0} level="HIGH" />
            <StatCard label="Medium" value={summary.summary?.MEDIUM ?? 0} level="MEDIUM" />
            <StatCard label="Low" value={summary.summary?.LOW ?? 0} level="LOW" />
          </div>

          <div style={{ fontSize: 12, color: "#888", marginBottom: 8 }}>
            Last updated: {summary.generated_at || "—"}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {(summary.alerts || [])
              .slice()
              .reverse()
              .slice(0, 10)
              .map((alert) => (
                <div
                  key={alert.id}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    background: "#fff",
                    border: "1px solid #eee",
                    borderRadius: 8,
                    padding: "8px 12px",
                  }}
                >
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 500 }}>
                      {alert.type}
                    </div>
                    <div style={{ fontSize: 12, color: "#888" }}>
                      {alert.src_ip} · {alert.detail}
                    </div>
                  </div>
                  <SeverityBadge level={alert.severity} />
                </div>
              ))}

            {(!summary.alerts || summary.alerts.length === 0) && (
              <p style={{ fontSize: 13, color: "#888" }}>
                No alerts recorded yet.
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
