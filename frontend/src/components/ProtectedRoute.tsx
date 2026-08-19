import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Layout } from "./Layout";

export function ProtectedRoute() {
  const { profile } = useAuth();
  if (!profile) return <Navigate to="/login" replace />;
  return <Layout />;
}
