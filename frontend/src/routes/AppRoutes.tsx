import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import DashboardLayout from "../layouts/DashboardLayout";
import AuthLayout from "../layouts/AuthLayout";
import ProtectedRoute from "./ProtectedRoute";
import PublicRoute from "./PublicRoute";
import { Skeleton } from "../components/ui/Skeleton";

const LoginPage = lazy(() => import("../modules/auth/LoginPage"));
const RegisterPage = lazy(() => import("../modules/auth/RegisterPage"));
const DashboardPage = lazy(() => import("../modules/dashboard/DashboardPage"));
const MonitoringPage = lazy(() => import("../modules/monitoring/MonitoringPage"));
const IncidentsPage = lazy(() => import("../modules/incidents/IncidentsPage"));
const IncidentDetailsPage = lazy(() => import("../modules/incidents/IncidentDetailsPage"));
const AIInvestigationPage = lazy(() => import("../modules/investigation/AIInvestigationPage"));
const LogsPage = lazy(() => import("../modules/logs/LogsPage"));
const ContainersPage = lazy(() => import("../modules/containers/ContainersPage"));
const ContainerLogsPage = lazy(() => import("../modules/containers/ContainerLogsPage"));
const RecommendationsPage = lazy(() => import("../modules/recommendations/RecommendationsPage"));
const KnowledgeBasePage = lazy(() => import("../modules/knowledge/KnowledgeBasePage"));
const AnalyticsPage = lazy(() => import("../modules/analytics/AnalyticsPage"));
const ReportsPage = lazy(() => import("../modules/reports/ReportsPage"));
const SettingsPage = lazy(() => import("../modules/settings/SettingsPage"));
const ProfilePage = lazy(() => import("../modules/profile/ProfilePage"));

function PageLoader() {
  return (
    <div className="p-6 space-y-4">
      <Skeleton height="h-8" width="w-64" />
      <Skeleton height="h-4" width="w-48" />
      <div className="grid grid-cols-4 gap-4 mt-6">
        {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} height="h-28" />)}
      </div>
      <Skeleton height="h-64" />
    </div>
  );
}

export default function AppRoutes() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route element={<PublicRoute />}>
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/monitoring" element={<MonitoringPage />} />
            <Route path="/incidents" element={<IncidentsPage />} />
            <Route path="/incidents/:id" element={<IncidentDetailsPage />} />
            <Route path="/containers" element={<ContainersPage />} />
            <Route path="/containers/:containerName" element={<ContainerLogsPage />} />
            <Route path="/logs" element={<LogsPage />} />
            <Route path="/ai-investigation" element={<AIInvestigationPage />} />
            <Route path="/recommendations" element={<RecommendationsPage />} />
            <Route path="/knowledge-base" element={<KnowledgeBasePage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Suspense>
  );
}
