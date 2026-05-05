import { useEffect, useMemo, useState } from "react";
import { getUsers, updateUserRole, updateUserStatus, getUserRole, getCurrentUserEmail } from "../services/api";
import { useNavigate } from "react-router-dom";
import "./AdminUsers.css";

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentUserEmail, setCurrentUserEmail] = useState(null);
  const navigate = useNavigate();

  const adminCount = useMemo(
    () => users.filter((user) => user.role === "admin").length,
    [users]
  );

  const activeCount = useMemo(
    () => users.filter((user) => user.is_active).length,
    [users]
  );

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/");
        return;
      }

      const role = getUserRole();
      setCurrentUserEmail(getCurrentUserEmail());
      if (role !== "admin") {
        navigate("/");
        return;
      }

      const response = await getUsers();
      setUsers(Array.isArray(response?.data) ? response.data : []);
      setError("");
    } catch (err) {
      setError(err?.message || "Unable to load users.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [navigate]);

  const refreshAfterMutation = async () => {
    await fetchUsers();
  };

  const handleRoleChange = async (userId, nextRole) => {
    try {
      setError("");
      await updateUserRole(userId, nextRole);
      await refreshAfterMutation();
    } catch (err) {
      setError(err?.message || "Role update failed.");
    }
  };

  const handleStatusChange = async (userId, currentStatus) => {
    try {
      setError("");
      const nextStatus = !currentStatus;
      const ok = window.confirm(
        nextStatus
          ? "Activate this user account?"
          : "Deactivate this user account?"
      );
      if (!ok) return;

      await updateUserStatus(userId, nextStatus);
      await refreshAfterMutation();
    } catch (err) {
      setError(err?.message || "Status update failed.");
    }
  };

  return (
    <div className="admin-page">
      <header className="admin-header">
        <div>
          <p className="eyebrow">NetGuardViz Admin Console</p>
          <h1 className="admin-title">User Management</h1>
          <p className="admin-subtext">
            Manage roles and account status for application users.
          </p>
        </div>

        <div className="admin-actions">
          <button className="btn btn-secondary" onClick={() => navigate("/dashboard")}>
            Dashboard
          </button>
          <button className="btn btn-secondary" onClick={() => navigate("/alerts")}>
            Alerts
          </button>
          <button className="btn btn-secondary" onClick={() => navigate("/logs")}>
            Logs
          </button>
        </div>
      </header>

      {error && <p className="error-banner">{error}</p>}

      <section className="summary-row">
        <article className="summary-card">
          <p>Total Users</p>
          <h2>{users.length}</h2>
        </article>
        <article className="summary-card">
          <p>Active Users</p>
          <h2>{activeCount}</h2>
        </article>
        <article className="summary-card">
          <p>Admins</p>
          <h2>{adminCount}</h2>
        </article>
      </section>

      <section className="admin-card">
        <div className="section-head">
          <h3>Registered Users</h3>
        </div>

        {loading ? (
          <p className="empty-state">Loading users...</p>
        ) : users.length === 0 ? (
          <p className="empty-state">No users found.</p>
        ) : (
          <div className="users-grid">
            {users.map((user) => {
              const isSelf = currentUserEmail && user.email === currentUserEmail;
              return (
                <article className="user-card" key={user.id}>
                  <div className="user-top">
                    <div>
                      <h3>{user.username || "Unnamed User"}</h3>
                      <p className="user-meta">{user.email}</p>
                    </div>
                    <span className={`pill ${user.role === "admin" ? "pill-warn" : user.is_active ? "pill-safe" : "pill-danger"}`}>
                      {user.role}
                    </span>
                  </div>

                  <p className="user-meta">
                    Status: <strong>{user.is_active ? "Active" : "Inactive"}</strong>
                  </p>

                  <div className="control-row">
                    <select
                      className="role-select"
                      value={user.role}
                      disabled={isSelf}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                    >
                      <option value="user">user</option>
                      <option value="admin">admin</option>
                    </select>

                    <button
                      className="btn btn-secondary"
                      onClick={() => handleStatusChange(user.id, user.is_active)}
                      disabled={isSelf}
                    >
                      {user.is_active ? "Deactivate" : "Activate"}
                    </button>

                    <button
                      className="btn btn-primary"
                      onClick={() => navigate("/dashboard")}
                    >
                      View
                    </button>
                  </div>

                  <p className="tiny-note">
                    Role changes and account status updates apply immediately.
                  </p>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}