const BASE_URL = "http://127.0.0.1:8000";

// Helper
const getToken = () => localStorage.getItem("token");

const parseJsonSafe = async (res) => {
  try {
    return await res.json();
  } catch {
    return null;
  }
};

const request = async (path, options = {}) => {
  const res = await fetch(`${BASE_URL}${path}`, options);
  const data = await parseJsonSafe(res);

  if (!res.ok) {
    throw new Error(data?.detail || `Request failed (${res.status})`);
  }

  return data;
};

// AUTH
export const signup = async (data) => {
  return request(`/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
};

export const login = async (data) => {
  return request(`/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
};

// LOGS
export const getLogs = async () => {
  return request(`/api/logs/`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
};

export const uploadLog = async (file) => {
  const formData = new FormData();
  formData.append("uploaded_file", file);

  return request(`/api/logs/upload`, {
    method: "POST",
    headers: { Authorization: `Bearer ${getToken()}` },
    body: formData,
  });
};

export const deleteLog = async (logId) => {
  return request(`/api/logs/${logId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${getToken()}` },
  });
};

// ALERTS
export const getAlerts = async () => {
  return request(`/api/alerts/`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
};

export const deleteAlert = async (alertId) => {
  return request(`/api/alerts/${alertId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${getToken()}` },
  });
};

// STATS
export const getStats = async () => {
  return request(`/api/stats/`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
};

// ADMIN USERS
export const getUsers = async () => {
  return request(`/auth/users`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
};

export const updateUserRole = async (userId, role) => {
  return request(`/auth/users/${userId}/role`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ role }),
  });
};

export const updateUserStatus = async (userId, isActive) => {
  return request(`/auth/users/${userId}/status`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ is_active: isActive }),
  });
};

// JWT helpers (client-side only - backend must enforce RBAC)
export const parseJwt = (token) => {
  if (!token) return null;
  try {
    const base64Url = token.split(".")[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => `%${(`00${c.charCodeAt(0).toString(16)}`).slice(-2)}`)
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
};

export const getUserRole = () => {
  const t = getToken();
  if (!t) return null;
  const parsed = parseJwt(t);
  return parsed?.role ?? null;
};

export const getCurrentUserEmail = () => {
  const t = getToken();
  if (!t) return null;
  const parsed = parseJwt(t);
  return parsed?.sub ?? null;
};