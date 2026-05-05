import { Navigate } from "react-router-dom";
import { getUserRole } from "../services/api";

export default function ProtectedRoute({ children, role }) {
  const token = localStorage.getItem("token");

  if (!token) {
    return <Navigate to="/" />;
  }

  if (role) {
    const userRole = getUserRole();
    if (userRole !== role) {
      return <Navigate to="/" />;
    }
  }

  return children;
}