import { Navigate, Outlet } from "react-router-dom";
import useAuthStore, { type AuthState } from "../store/authStore";

export default function PublicRoute() {
  const isAuthenticated = useAuthStore((state: AuthState) => state.isAuthenticated);

  // Condition B: If an authenticated user tries to access /login or /register, redirect to /dashboard
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}

