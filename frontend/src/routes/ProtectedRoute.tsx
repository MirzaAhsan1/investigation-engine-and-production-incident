import { Navigate, Outlet } from "react-router-dom";
import useAuthStore, { type AuthState } from "../store/authStore";

export default function ProtectedRoute() {
  const isAuthenticated = useAuthStore((state: AuthState) => state.isAuthenticated);

  // Condition A: If a user attempts to access a protected page without a token, redirect them to /login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

