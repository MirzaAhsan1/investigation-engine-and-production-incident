import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Sparkles,
  Clock,
  Server,
  CheckCircle2,
  AlertTriangle,
  Terminal,
  Activity,
  MessageSquare,
  Plus,
  Cpu,
  Database,
  Layers,
  X,
  FileCode,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Tabs } from "../../components/ui/Tabs";
import { useGetIncidentByIdQuery } from "../../api/incidentsApi";
import { useCreateEvidenceMutation, useGetEvidenceByIncidentQuery } from "../../api/evidenceApi";
import {
  useStartInvestigationMutation,
  useGetInvestigationByIncidentQuery,
  useGetInvestigationReportQuery,
} from "../../api/investigationApi";
import { useGetInvestigationActionsQuery } from "../../api/actionsApi";
import { InvestigationSummary } from "../../components/ui/InvestigationSummary";
import { InvestigationReasoning } from "../../components/ui/InvestigationReasoning";
import { RecommendedActionsTable } from "../../components/ui/RecommendedActionsTable";

const staticIncidentData: Record<string, any> = {
  "INC-1041": {
    id: "INC-1041",
    title: "Database Connection Pool Exhausted – postgres-primary",
    severity: "P0",
    status: "OPEN",
    service: "postgres-primary",
    environment: "production",
    region: "us-east-1",
    assignee: "Unassigned",
    createdAt: "2026-07-23 19:29 UTC",
    updatedAt: "2026-07-23 19:58 UTC",
    description: "The postgres-primary database connection pool is fully exhausted. All 200/200 connections are in use. New connection requests are timing out after 30s, causing cascading failures across payment-svc and api-gateway.",
    aiReasoning: {
      hypothesis: "Root cause is a runaway background job in the analytics pipeline that opened and leaked ~180 database connections without releasing them. This coincides with a deploy at 19:15 UTC that introduced a missing `finally: db.close()` call in the reporting batch worker.",
      confidence: 97,
      riskLevel: "CRITICAL",
      recommendedFix: "1. Immediately kill all idle connections older than 10 minutes via `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND query_start < NOW() - INTERVAL '10 minutes';` 2. Scale down analytics-worker to 0 replicas. 3. Deploy hotfix to patch the connection leak.",
    },
    logs: [
      { timestamp: "19:29:01 UTC", level: "ERROR", message: "FATAL: remaining connection slots are reserved for non-replication superuser connections", source: "postgres-primary" },
      { timestamp: "19:29:05 UTC", level: "ERROR", message: "connection pool exhausted: no available connections after 30000ms", source: "payment-svc" },
      { timestamp: "19:29:12 UTC", level: "WARN", message: "max_connections=200, current active=200", source: "postgres-primary" },
      { timestamp: "19:29:18 UTC", level: "ERROR", message: "PoolTimeoutError: QueuePool limit of 200 overflow reached", source: "api-gateway" },
      { timestamp: "19:15:44 UTC", level: "INFO", message: "Deployment analytics-worker v1.4.2 → v1.4.3 completed", source: "k8s-deploy" },
    ],
    timeline: [
      { time: "19:15 UTC", type: "ACTION_TAKEN", title: "analytics-worker v1.4.3 deployed" },
      { time: "19:29 UTC", type: "DETECTED", title: "Connection pool exhausted – automated alert triggered" },
      { time: "19:32 UTC", type: "AI_DIAGNOSED", title: "AI identified connection leak in analytics-worker" },
    ],
  },
};

const logColors: Record<string, string> = {
  ERROR: "text-rose-400",
  WARN: "text-amber-400",
  INFO: "text-slate-400",
};

const timelineIcons: Record<string, React.ReactNode> = {
  DETECTED: <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />,
  AI_DIAGNOSED: <Sparkles className="w-3.5 h-3.5 text-violet-400" />,
  ACTION_TAKEN: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />,
};

const severityMap: Record<string, string> = {
  CRITICAL: "P0",
  HIGH: "P1",
  MEDIUM: "P2",
  LOW: "P3",
};

export default function IncidentDetailsPage() {
  const { id = "" } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("overview");

  // UUID detector helper
  const isUuid = id.length > 20;

  // Backend RTK Queries
  const { data: backendIncident } = useGetIncidentByIdQuery(id, { skip: !isUuid });
  const { data: backendEvidence } = useGetEvidenceByIncidentQuery(id, { skip: !isUuid });
  const { data: backendInvestigation } = useGetInvestigationByIncidentQuery(id, { skip: !isUuid });
  useGetInvestigationReportQuery(id, { skip: !isUuid });

  const investigationId = backendInvestigation?.id || "";
  const {
    data: investigationActions,
    isLoading: isLoadingActions,
    error: actionsError,
  } = useGetInvestigationActionsQuery(investigationId, { skip: !investigationId });

  // Mutations
  const [createEvidence, { isLoading: isSubmittingEvidence }] = useCreateEvidenceMutation();
  const [startInvestigation, { isLoading: isInvestigating }] = useStartInvestigationMutation();

  // Modals & Form state
  const [isEvidenceModalOpen, setIsEvidenceModalOpen] = useState(false);
  const [evidenceSuccess, setEvidenceSuccess] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const defaultEvidenceForm = {
    cpu_usage: 94.5,
    memory_usage: 88.2,
    disk_usage: 75.0,
    disk_io_wait: 0.0,
    api_latency: 3400,
    network_latency: 0,
    packet_loss: 0.0,
    request_per_second: 0,
    error_rate: 14.8,
    http_5xx_count: 0,
    http_4xx_count: 0,
    restart_count: 0,
    pod_restart_count: 0,
    active_containers: 2,
    deployment_changed: false,
    db_connections: 450,
    database_timeout_count: 0,
    failed_login_attempts: 0,
    ssl_certificate_days_left: 365,
    service_name: "backend-api",
    environment: "production",
    logs: "[ERROR] connection pool exhausted: DB connection timeout after 30000ms in payment-svc",
  };
  const [evidenceForm, setEvidenceForm] = useState(defaultEvidenceForm);

  // Evidence has been attached (either from API or just submitted)
  const hasEvidence = !!backendEvidence || evidenceSuccess;

  // Hybrid Data Fallback Resolution
  const staticFallback = staticIncidentData[id] || staticIncidentData["INC-1041"];

  const incident = backendIncident
    ? {
        id: backendIncident.id,
        title: backendIncident.title,
        severity: severityMap[backendIncident.severity] || backendIncident.severity,
        status: backendIncident.status,
        service: backendIncident.incident_type.toLowerCase() + "-svc",
        environment: "production",
        region: "us-east-1",
        assignee: "SRE On-Call",
        createdAt: new Date(backendIncident.created_at).toISOString().slice(0, 16).replace("T", " ") + " UTC",
        updatedAt: new Date(backendIncident.updated_at).toISOString().slice(0, 16).replace("T", " ") + " UTC",
        description: backendIncident.description,
        aiReasoning: backendInvestigation
          ? {
              hypothesis: backendInvestigation.root_cause || backendInvestigation.reasoning || "AI Root Cause Investigation Completed",
              confidence: Math.round(backendInvestigation.confidence || backendInvestigation.llm_confidence || 95),
              riskLevel: backendInvestigation.predicted_category || "CRITICAL",
              recommendedFix: backendInvestigation.recommended_actions,
            }
          : staticFallback.aiReasoning,
        logs: backendEvidence
          ? [
              {
                timestamp: new Date(backendEvidence.created_at).toISOString().slice(11, 19) + " UTC",
                level: "ERROR",
                message: typeof backendEvidence.logs === "string" ? backendEvidence.logs : JSON.stringify(backendEvidence.logs),
                source: backendIncident.incident_type.toLowerCase() + "-svc",
              },
              ...staticFallback.logs,
            ]
          : staticFallback.logs,
        timeline: staticFallback.timeline,
      }
    : staticFallback;

  const handleAddEvidenceSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    setApiError(null);
    try {
      await createEvidence({
        incident_id: id,
        cpu_usage: Number(evidenceForm.cpu_usage),
        memory_usage: Number(evidenceForm.memory_usage),
        disk_usage: Number(evidenceForm.disk_usage),
        disk_io_wait: Number(evidenceForm.disk_io_wait),
        api_latency: Number(evidenceForm.api_latency),
        network_latency: Number(evidenceForm.network_latency),
        packet_loss: Number(evidenceForm.packet_loss),
        request_per_second: Number(evidenceForm.request_per_second),
        error_rate: Number(evidenceForm.error_rate),
        http_5xx_count: Number(evidenceForm.http_5xx_count),
        http_4xx_count: Number(evidenceForm.http_4xx_count),
        restart_count: Number(evidenceForm.restart_count),
        pod_restart_count: Number(evidenceForm.pod_restart_count),
        active_containers: Number(evidenceForm.active_containers),
        deployment_changed: Boolean(evidenceForm.deployment_changed),
        db_connections: Number(evidenceForm.db_connections),
        database_timeout_count: Number(evidenceForm.database_timeout_count),
        failed_login_attempts: Number(evidenceForm.failed_login_attempts),
        ssl_certificate_days_left: Number(evidenceForm.ssl_certificate_days_left),
        service_name: evidenceForm.service_name,
        environment: evidenceForm.environment,
        logs: evidenceForm.logs,
      }).unwrap();

      setEvidenceSuccess(true);
      setEvidenceForm(defaultEvidenceForm);
      setTimeout(() => {
        setIsEvidenceModalOpen(false);
      }, 1200);
    } catch (err: any) {
      setApiError(err?.data?.detail || "Failed to add evidence. Please check the backend connection.");
    }
  };

  const handleRunInvestigation = async () => {
    if (!id) return;
    setApiError(null);
    try {
      await startInvestigation({ incident_id: id }).unwrap();
      setActiveTab("ai");
    } catch (err: any) {
      setApiError(err?.data?.detail || "AI Investigation failed. Ensure evidence is attached and the backend is running.");
    }
  };

  const tabs = [
    { id: "overview", label: "Overview", icon: <Activity className="w-3.5 h-3.5" /> },
    { id: "evidence", label: "Evidence & Metrics", icon: <Cpu className="w-3.5 h-3.5" /> },
    { id: "logs", label: "Live Logs", badge: incident.logs.length, icon: <Terminal className="w-3.5 h-3.5" /> },
    { id: "ai", label: "AI Investigation", icon: <Sparkles className="w-3.5 h-3.5" /> },
    { id: "timeline", label: "Timeline", icon: <Clock className="w-3.5 h-3.5" /> },
    { id: "notes", label: "Notes", icon: <MessageSquare className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className="space-y-5 max-w-6xl">
      {/* Back Navigation */}
      <button
        onClick={() => navigate("/incidents")}
        className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Incidents
      </button>

      {/* Incident Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-2.5 mb-2 flex-wrap">
            <span className="text-xs font-mono font-bold text-indigo-400 truncate max-w-[180px]">{incident.id}</span>
            <Badge variant="severity" severity={incident.severity}>{incident.severity}</Badge>
            <Badge variant="status" status={incident.status}>{incident.status}</Badge>
          </div>
          <h1 className="text-xl font-bold text-slate-50 tracking-tight">{incident.title}</h1>
          <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-slate-400">
            <span className="flex items-center gap-1.5"><Server className="w-3.5 h-3.5" />{incident.service}</span>
            <span>·</span>
            <span>{incident.region}</span>
            <span>·</span>
            <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" />Created {incident.createdAt}</span>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <Button
            variant="secondary"
            size="sm"
            leftIcon={<Plus className="w-3.5 h-3.5" />}
            onClick={() => { setApiError(null); setIsEvidenceModalOpen(true); }}
          >
            Add Evidence
          </Button>

          {/* Analyze / Investigation Option */}
          {hasEvidence && (
            <Button
              variant="ai"
              size="sm"
              isLoading={isInvestigating}
              leftIcon={<Sparkles className="w-3.5 h-3.5" />}
              onClick={handleRunInvestigation}
            >
              {isInvestigating ? "Analyzing..." : "Analyze with AI"}
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      {/* Error Feedback Banner */}
      {apiError && (
        <div className="flex items-center justify-between p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-xs">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>{apiError}</span>
          </div>
          <button onClick={() => setApiError(null)} className="p-0.5 hover:text-white transition-colors">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Tab Content */}
      {activeTab === "overview" && (
        <Card>
          <CardHeader>
            <CardTitle>Incident Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-300 leading-relaxed">{incident.description}</p>
            <div className="mt-5 grid grid-cols-2 sm:grid-cols-3 gap-4 pt-4 border-t border-slate-800/60">
              {[
                { label: "Environment", value: incident.environment },
                { label: "Assignee", value: incident.assignee },
                { label: "Last Updated", value: incident.updatedAt },
              ].map((f) => (
                <div key={f.label}>
                  <p className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">{f.label}</p>
                  <p className="text-sm text-slate-200 font-medium">{f.value}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === "evidence" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-200">System Telemetry & Evidence Artifacts</h3>
            <Button
              variant="secondary"
              size="sm"
              leftIcon={<Plus className="w-3.5 h-3.5" />}
              onClick={() => setIsEvidenceModalOpen(true)}
            >
              Add New Telemetry Evidence
            </Button>
          </div>

          <div className="space-y-6">
            {/* Infrastructure Metrics */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5 font-mono">
                <Cpu className="w-3.5 h-3.5" /> Infrastructure Telemetry
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">CPU Usage</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.cpu_usage ?? 94.5}%</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">Memory Usage</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.memory_usage ?? 88.2}%</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">Disk Usage</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.disk_usage ?? 75.0}%</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">Disk IO Wait</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.disk_io_wait ?? 0.0}%</p>
                </div>
              </div>
            </div>

            {/* Application & Traffic Metrics */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5 font-mono">
                <Activity className="w-3.5 h-3.5" /> Application & Traffic
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">API Latency</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.api_latency ?? 3400} ms</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">Error Rate</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.error_rate ?? 14.8}%</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">Requests Per Second</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.request_per_second ?? 0}</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">HTTP 5xx Errors</span>
                  <p className="text-base font-bold text-rose-400">{backendEvidence?.http_5xx_count ?? 0}</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">HTTP 4xx Errors</span>
                  <p className="text-base font-bold text-amber-400">{backendEvidence?.http_4xx_count ?? 0}</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">Restart Count</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.restart_count ?? 0}</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">Pod Restart Count</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.pod_restart_count ?? 0}</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">Active Containers</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.active_containers ?? 2}</p>
                </div>
              </div>
            </div>

            {/* Database & Network */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5 font-mono">
                <Database className="w-3.5 h-3.5" /> Database & Network
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">DB Connections</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.db_connections ?? 450}</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">DB Timeout Count</span>
                  <p className="text-base font-bold text-rose-400">{backendEvidence?.database_timeout_count ?? 0}</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">Network Latency</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.network_latency ?? 0} ms</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">Packet Loss</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.packet_loss ?? 0.0}%</p>
                </div>
              </div>
            </div>

            {/* Security & Service Context */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-violet-400 flex items-center gap-1.5 font-mono">
                <Layers className="w-3.5 h-3.5" /> Security & Context
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">Failed Logins</span>
                  <p className="text-base font-bold text-rose-400">{backendEvidence?.failed_login_attempts ?? 0}</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">SSL Cert Days Left</span>
                  <p className="text-base font-bold text-slate-100">{backendEvidence?.ssl_certificate_days_left ?? 365}</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">Service Name</span>
                  <p className="text-sm font-bold text-slate-300 truncate">{backendEvidence?.service_name ?? "backend-api"}</p>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-1">
                  <span className="text-slate-400 font-medium">Environment / Deploy</span>
                  <p className="text-xs font-bold text-slate-300">
                    {backendEvidence?.environment ?? "production"}
                    {backendEvidence?.deployment_changed && <span className="ml-1 text-[10px] text-amber-400 font-mono font-bold">(CHANGED)</span>}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle><FileCode className="w-4 h-4 text-indigo-400" /> Collected Log Evidence</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="font-mono text-xs bg-slate-950 p-4 rounded-xl border border-slate-800 text-rose-300 leading-relaxed overflow-x-auto">
                {backendEvidence?.logs ? (typeof backendEvidence.logs === "string" ? backendEvidence.logs : JSON.stringify(backendEvidence.logs, null, 2)) : evidenceForm.logs}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === "logs" && (
        <Card>
          <CardHeader>
            <CardTitle><Terminal className="w-4 h-4 text-emerald-400" />Live Log Stream</CardTitle>
          </CardHeader>
          <CardContent padding="none">
            <div className="font-mono text-xs bg-slate-950 rounded-b-xl overflow-x-auto">
              {incident.logs.map((log: any, i: number) => (
                <div key={i} className="flex items-start gap-3 px-5 py-2.5 border-b border-slate-800/40 hover:bg-slate-900/50 transition-colors">
                  <span className="text-slate-600 flex-shrink-0">{log.timestamp}</span>
                  <span className={`font-bold flex-shrink-0 w-10 ${logColors[log.level] || "text-slate-300"}`}>{log.level}</span>
                  <span className="text-slate-400 flex-shrink-0 hidden sm:inline">[{log.source}]</span>
                  <span className={logColors[log.level] || "text-slate-300"}>{log.message}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === "ai" && (
        <div className="space-y-6">
          {backendInvestigation ? (
            <>
              <InvestigationSummary investigation={backendInvestigation} />
              <InvestigationReasoning investigation={backendInvestigation} />
              <RecommendedActionsTable
                actions={investigationActions || []}
                isLoading={isLoadingActions}
                error={actionsError ? "Failed to load recommended action queue" : null}
              />
            </>
          ) : (
            <Card variant="glow">
              <CardHeader>
                <CardTitle><Sparkles className="w-4 h-4 text-violet-400" />AI Root Cause Analysis & Reasoning</CardTitle>
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-20 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full"
                      style={{ width: `${incident.aiReasoning.confidence}%` }}
                    />
                  </div>
                  <span className="text-xs font-bold text-violet-300">{incident.aiReasoning.confidence}% Confidence</span>
                </div>
              </CardHeader>

              <CardContent>
                <div className="p-4 bg-slate-950/80 rounded-xl border border-violet-500/10">
                  <p className="text-sm font-semibold text-violet-400 mb-1">Root Cause / Hypothesis</p>
                  <p className="text-sm text-slate-200 leading-relaxed">{incident.aiReasoning.hypothesis}</p>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-800/60">
                  <p className="text-xs font-semibold text-slate-300 mb-2">Recommended Actions & Solutions</p>
                  <div className="font-mono text-xs bg-slate-950 border border-slate-800 rounded-xl p-4 text-emerald-300 whitespace-pre-wrap leading-relaxed">
                    {incident.aiReasoning.recommendedFix}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {activeTab === "timeline" && (
        <Card>
          <CardHeader>
            <CardTitle><Clock className="w-4 h-4 text-indigo-400" />Incident Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative pl-5 border-l-2 border-slate-800 space-y-5">
              {incident.timeline.map((event: any, i: number) => (
                <div key={i} className="relative flex items-start gap-3">
                  <div className="absolute -left-6 top-0 w-5 h-5 rounded-full bg-slate-900 border-2 border-slate-700 flex items-center justify-center">
                    {timelineIcons[event.type]}
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-slate-200">{event.title}</p>
                    <p className="text-[11px] text-slate-500 mt-0.5">{event.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === "notes" && (
        <Card>
          <CardHeader>
            <CardTitle><MessageSquare className="w-4 h-4 text-indigo-400" />Engineer Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <textarea
              rows={6}
              placeholder="Add investigation notes, hypothesis, or actions taken..."
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 resize-none"
            />
            <div className="flex justify-end mt-3">
              <Button variant="secondary" size="sm">Save Notes</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Add Evidence Modal */}
      {isEvidenceModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm overflow-y-auto">
          <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4 my-8">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Cpu className="w-5 h-5 text-indigo-400" /> Add Telemetry Evidence & Logs
              </h3>
              <button
                onClick={() => setIsEvidenceModalOpen(false)}
                className="p-1 text-slate-400 hover:text-white rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {evidenceSuccess && (
              <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" /> Evidence added! Click 'Analyze with AI' to trigger AI investigation.
              </div>
            )}

            <form onSubmit={handleAddEvidenceSubmit} className="space-y-4 text-xs">
              {/* Infrastructure section */}
              <div className="space-y-2">
                <p className="font-bold text-indigo-400 uppercase tracking-wider text-[10px] font-mono">1. Infrastructure Metrics</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">CPU Usage (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      required
                      value={evidenceForm.cpu_usage}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, cpu_usage: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Memory (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      required
                      value={evidenceForm.memory_usage}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, memory_usage: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Disk (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      required
                      value={evidenceForm.disk_usage}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, disk_usage: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Disk IO Wait (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      required
                      value={evidenceForm.disk_io_wait}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, disk_io_wait: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Application section */}
              <div className="space-y-2">
                <p className="font-bold text-rose-400 uppercase tracking-wider text-[10px] font-mono">2. Application & Traffic</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">API Latency (ms)</label>
                    <input
                      type="number"
                      required
                      value={evidenceForm.api_latency}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, api_latency: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Error Rate (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      required
                      value={evidenceForm.error_rate}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, error_rate: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">RPS</label>
                    <input
                      type="number"
                      required
                      value={evidenceForm.request_per_second}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, request_per_second: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">HTTP 5xx Count</label>
                    <input
                      type="number"
                      required
                      value={evidenceForm.http_5xx_count}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, http_5xx_count: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">HTTP 4xx Count</label>
                    <input
                      type="number"
                      required
                      value={evidenceForm.http_4xx_count}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, http_4xx_count: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Restart Count</label>
                    <input
                      type="number"
                      required
                      value={evidenceForm.restart_count}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, restart_count: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Pod Restart Count</label>
                    <input
                      type="number"
                      required
                      value={evidenceForm.pod_restart_count}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, pod_restart_count: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Active Containers</label>
                    <input
                      type="number"
                      required
                      value={evidenceForm.active_containers}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, active_containers: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Database & Network section */}
              <div className="space-y-2">
                <p className="font-bold text-amber-400 uppercase tracking-wider text-[10px] font-mono">3. Database & Network</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">DB Connections</label>
                    <input
                      type="number"
                      required
                      value={evidenceForm.db_connections}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, db_connections: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">DB Timeout Count</label>
                    <input
                      type="number"
                      required
                      value={evidenceForm.database_timeout_count}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, database_timeout_count: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Network Latency (ms)</label>
                    <input
                      type="number"
                      required
                      value={evidenceForm.network_latency}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, network_latency: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Packet Loss (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      required
                      value={evidenceForm.packet_loss}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, packet_loss: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Security & Service Info section */}
              <div className="space-y-2">
                <p className="font-bold text-violet-400 uppercase tracking-wider text-[10px] font-mono">4. Security & Context</p>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Failed Logins</label>
                    <input
                      type="number"
                      required
                      value={evidenceForm.failed_login_attempts}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, failed_login_attempts: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">SSL Days Left</label>
                    <input
                      type="number"
                      required
                      value={evidenceForm.ssl_certificate_days_left}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, ssl_certificate_days_left: Number(e.target.value) })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Service Name</label>
                    <input
                      type="text"
                      required
                      value={evidenceForm.service_name}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, service_name: e.target.value })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Environment</label>
                    <input
                      type="text"
                      required
                      value={evidenceForm.environment}
                      onChange={(e) => setEvidenceForm({ ...evidenceForm, environment: e.target.value })}
                      className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none"
                    />
                  </div>
                  <div className="flex flex-col justify-end">
                    <label className="flex items-center gap-2 py-2.5 cursor-pointer text-slate-300 font-semibold">
                      <input
                        type="checkbox"
                        checked={evidenceForm.deployment_changed}
                        onChange={(e) => setEvidenceForm({ ...evidenceForm, deployment_changed: e.target.checked })}
                        className="rounded border-slate-850 bg-slate-950 text-indigo-500 focus:ring-indigo-500"
                      />
                      Deployment Changed
                    </label>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Application Logs</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Paste error logs, stacktraces, or telemetry messages..."
                  value={evidenceForm.logs}
                  onChange={(e) => setEvidenceForm({ ...evidenceForm, logs: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none resize-none font-mono"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <Button variant="secondary" type="button" size="sm" onClick={() => setIsEvidenceModalOpen(false)}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit" size="sm" isLoading={isSubmittingEvidence}>
                  Save Evidence
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
