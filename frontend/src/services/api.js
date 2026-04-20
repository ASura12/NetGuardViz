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