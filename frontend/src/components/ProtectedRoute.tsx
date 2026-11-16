import { Navigate } from "react-router-dom";
import { Spin } from "antd";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { me, loading } = useAuth();

  if (loading) return <Spin style={{ margin: 48 }} />;
  if (!me) return <Navigate to="/login" replace />;
  return <>{children}</>;
}