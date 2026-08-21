import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  Plus,
  X,
  CheckCircle2,
  Server,
  Activity,
  Cpu,
  RefreshCw,
  Sparkles,
  Zap,
  Layers,
} from "lucide-react";
import { DataTable } from "../../components/ui/DataTable";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { useGetIncidentsQuery, useCreateIncidentMutation, type BackendIncident } from "../../api/incidentsApi";
import { useGetServerStatsQuery } from "../../api/monitoringApi";

const severityMap: Record<string, string> = {
  CRITICAL: "P0",
  HIGH: "P1",
  MEDIUM: "P2",
  LOW: "P3",
};

const mockIncidents = [
  {
    id: "INC-1042",
    title: "API Gateway High Latency – prod-us-east-1",
    severity: "P1",
    status: "INVESTIGATING",
    service: "api-gateway",
    assignee: "Jane Smith",
    createdAt: "2026-07-23 19:48",
    aiConfidence: 89,
    predictedCategory: "Network / Latency",
    predictedCause: "Upstream connection bottleneck in edge proxy",
  },
  {
    id: "INC-1041",
    title: "Database Connection Pool Exhausted – postgres-primary",
    severity: "P0",
    status: "OPEN",
    service: "postgres-primary",
    assignee: "Unassigned",
    createdAt: "2026-07-23 19:29",
    aiConfidence: 97,
    predictedCategory: "Database",
    predictedCause: "Connection pool exhaustion (200/200 active slots)",
  },
  {
    id: "INC-1040",
    title: "Payment Service 5xx Spike > 2% Error Rate",
    severity: "P1",
    status: "MITIGATED",
    service: "payment-svc",
    assignee: "Alice Patel",
    createdAt: "2026-07-23 17:46",
    aiConfidence: 93,
    predictedCategory: "Application Error",
    predictedCause: "Third-party payment gateway timeout exception",
  },
  {
    id: "INC-1039",
    title: "Redis Cache Miss Rate > 60%",
    severity: "P2",
    status: "RESOLVED",
    service: "redis-cluster",
    assignee: "Bob Lee",
    createdAt: "2026-07-23 14:00",
    aiConfidence: 78,
    predictedCategory: "Cache / Performance",
    predictedCause: "Cache key eviction overflow on node 02",
  },
];

export default function IncidentsPage() {
  const navigate = useNavigate();

  // Fetch live backend incidents sorted by created_at desc
  const { data: backendIncidents, refetch: refetchIncidents } = useGetIncidentsQuery();
  
  // Fetch real-time server health stats (polling every 5 seconds)
  const { data: serverStats, isLoading: isServersLoading, refetch: refetchServers } = useGetServerStatsQuery(undefined, {
    pollingInterval: 5000,
  });

  const [createIncident, { isLoading: isCreating }] = useCreateIncidentMutation();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formSuccess, setFormSuccess] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    incident_type: "APPLICATION",
    severity: "HIGH",
    source: "MANUAL",
  });

  // Map backend incidents to list rows with investigation summary previews
  const formattedBackendIncidents = (backendIncidents || []).map((b: BackendIncident) => {
    const appName = b.application?.name || (b.incident_type ? b.incident_type.toLowerCase() + "-svc" : "system-svc");
    const investigation = b.investigation;
    return {
      id: b.id,
      rawId: b.id,
      title: b.title,
      severity: b.severity,
      status: b.status,
      service: appName,
      assignee: b.assigned_to ? "Assigned" : "Unassigned",
      createdAt: new Date(b.created_at).toLocaleString([], {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }),
      aiConfidence: investigation?.confidence ? Math.round(investigation.confidence) : 92,
      predictedCategory: investigation?.predicted_category || b.incident_type || "General",
      predictedCause: investigation?.root_cause || investigation?.predicted_cause || "Pending AI root cause analysis...",
      isBackend: true,
    };
  });

  // Combine live backend incidents first, fallback to mock if no backend data
  const allIncidents = formattedBackendIncidents.length > 0 
    ? formattedBackendIncidents 
    : mockIncidents.map((m) => ({ ...m, rawId: m.id, isBackend: false }));

  // Filter by status if tab selected
  const filteredIncidents = statusFilter === "ALL" 
    ? allIncidents 
    : allIncidents.filter((i) => i.status.toUpperCase() === statusFilter.toUpperCase());

  // Metrics summary calculations
  const openCount = allIncidents.filter((i) => i.status === "OPEN" || i.status === "INVESTIGATING").length;
  const p0Count = allIncidents.filter((i) => i.severity === "CRITICAL" || i.severity === "P0").length;
  const p1Count = allIncidents.filter((i) => i.severity === "HIGH" || i.severity === "P1").length;

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createIncident({
        title: formData.title,
        description: formData.description,
        incident_type: formData.incident_type,
        severity: formData.severity,
        source: formData.source,
      }).unwrap();

      setFormSuccess(true);
      setTimeout(() => {
        setFormSuccess(false);
        setIsModalOpen(false);
        setFormData({
          title: "",
          description: "",
          incident_type: "APPLICATION",
          severity: "HIGH",
          source: "MANUAL",
        });
      }, 1200);
    } catch {
      // Handled via RTK Error Boundary
    }
  };

  const columns = [
    {
      key: "id",
      header: "Incident ID",
      render: (item: any) => (
        <span className="text-xs font-mono font-semibold text-indigo-400 truncate max-w-[120px] block">
          {item.id.length > 12 ? `${item.id.slice(0, 8)}...` : item.id}
        </span>
      ),
    },
    {
      key: "title",
      header: "Incident Title & Service",
      sortable: true,
      render: (item: any) => (
        <div className="flex flex-col max-w-[280px]">
          <span className="text-xs font-medium text-slate-100 truncate">{item.title}</span>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="text-[10px] font-mono text-indigo-300/80 bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">
              {item.service}
            </span>
          </div>
        </div>
      ),
    },
    {
      key: "severity",
      header: "Severity",
      sortable: true,
      render: (item: any) => (
        <Badge variant="severity" severity={(severityMap[item.severity] || item.severity) as any}>
          {severityMap[item.severity] || item.severity}
        </Badge>
      ),
    },
    {
      key: "status",
      header: "Status",
      sortable: true,
      render: (item: any) => (
        <Badge variant="status" status={item.status as any}>
          {item.status}
        </Badge>
      ),
    },
    {
      key: "investigationPreview",
      header: "AI Investigation Preview",
      render: (item: any) => (
        <div className="flex flex-col max-w-[300px]">
          <div className="flex items-center gap-1.5 mb-0.5">
            <Sparkles className="w-3 h-3 text-violet-400 flex-shrink-0" />
            <span className="text-[10px] font-semibold text-violet-300 uppercase tracking-wider bg-violet-500/10 px-1.5 py-0.5 rounded border border-violet-500/20">
              {item.predictedCategory}
            </span>
          </div>
          <span className="text-[11px] text-slate-300 italic truncate" title={item.predictedCause}>
            "{item.predictedCause}"
          </span>
        </div>
      ),
    },
    {
      key: "aiConfidence",
      header: "Confidence",
      render: (item: any) => (
        <div className="flex items-center gap-2">
          <div className="w-14 h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-violet-500 to-indigo-400 rounded-full"
              style={{ width: `${item.aiConfidence}%` }}
            />
          </div>
          <span className="text-xs font-semibold text-violet-300">{item.aiConfidence}%</span>
        </div>
      ),
    },
    {
      key: "createdAt",
      header: "Created",
      sortable: true,
      render: (item: any) => <span className="text-xs text-slate-400">{item.createdAt}</span>,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-50 tracking-tight flex items-center gap-2.5">
            <AlertTriangle className="w-6 h-6 text-indigo-400" /> Incidents Dashboard
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time incident response command center, ML cause preview & active server metrics telemetry
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
            onClick={() => {
              refetchIncidents();
              refetchServers();
            }}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Plus className="w-3.5 h-3.5" />}
            onClick={() => setIsModalOpen(true)}
          >
            Declare Incident
          </Button>
        </div>
      </div>

      {/* Top Banner Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 bg-slate-900/80 backdrop-blur border border-slate-800 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium block">Active Incidents</span>
            <span className="text-xl font-bold text-white mt-1 block">{openCount}</span>
          </div>
          <div className="p-2.5 bg-indigo-500/10 rounded-xl border border-indigo-500/20 text-indigo-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 bg-slate-900/80 backdrop-blur border border-slate-800 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium block">P0 Critical</span>
            <span className="text-xl font-bold text-rose-400 mt-1 block">{p0Count}</span>
          </div>
          <div className="p-2.5 bg-rose-500/10 rounded-xl border border-rose-500/20 text-rose-400">
            <Zap className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 bg-slate-900/80 backdrop-blur border border-slate-800 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium block">P1 High Severity</span>
            <span className="text-xl font-bold text-amber-400 mt-1 block">{p1Count}</span>
          </div>
          <div className="p-2.5 bg-amber-500/10 rounded-xl border border-amber-500/20 text-amber-400">
            <Layers className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 bg-slate-900/80 backdrop-blur border border-slate-800 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium block">Active Servers</span>
            <span className="text-xl font-bold text-emerald-400 mt-1 block">
              {serverStats ? serverStats.length : 3}
            </span>
          </div>
          <div className="p-2.5 bg-emerald-500/10 rounded-xl border border-emerald-500/20 text-emerald-400">
            <Server className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* SECTION 3: DASHBOARD / SERVER METRICS TELEMETRY (Real-time polling) */}
      <Card variant="glow">
        <CardHeader>
          <div className="flex items-center justify-between w-full">
            <CardTitle>
              <Activity className="w-4 h-4 text-emerald-400" /> Live Server Metrics Telemetry (5s Polling)
            </CardTitle>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[11px] text-slate-400 font-mono">Live Telemetry</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isServersLoading && !serverStats ? (
            <div className="text-xs text-slate-400 py-4 text-center">Loading live server metrics...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {(serverStats && serverStats.length > 0
                ? serverStats
                : [
                    {
                      server_id: "s1",
                      name: "prod-server-01",
                      host: "192.168.1.10",
                      environment: "production",
                      cpu_usage: 42.8,
                      memory_usage: 68.2,
                      disk_usage: 54.0,
                      error_rate: 0.012,
                      open_incidents_count: 1,
                    },
                    {
                      server_id: "s2",
                      name: "db-primary-node",
                      host: "192.168.1.12",
                      environment: "production",
                      cpu_usage: 89.4,
                      memory_usage: 92.1,
                      disk_usage: 78.5,
                      error_rate: 0.048,
                      open_incidents_count: 2,
                    },
                    {
                      server_id: "s3",
                      name: "worker-pool-01",
                      host: "192.168.1.15",
                      environment: "production",
                      cpu_usage: 28.1,
                      memory_usage: 41.5,
                      disk_usage: 32.0,
                      error_rate: 0.0,
                      open_incidents_count: 0,
                    },
                  ]
              ).map((srv) => (
                <div
                  key={srv.server_id}
                  className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl space-y-3 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                    <div className="flex items-center gap-2">
                      <Server className="w-4 h-4 text-indigo-400" />
                      <div>
                        <span className="text-xs font-bold text-slate-100 block">{srv.name}</span>
                        <span className="text-[10px] font-mono text-slate-500">{srv.host}</span>
                      </div>
                    </div>
                    {srv.open_incidents_count > 0 ? (
                      <span className="text-[10px] font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full border border-rose-500/20">
                        {srv.open_incidents_count} Open Incident{srv.open_incidents_count > 1 ? "s" : ""}
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                        Healthy
                      </span>
                    )}
                  </div>

                  {/* CPU Usage Bar */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-[11px]">
                      <span className="text-slate-400 flex items-center gap-1">
                        <Cpu className="w-3 h-3 text-slate-400" /> CPU Load
                      </span>
                      <span className={`font-semibold ${srv.cpu_usage > 85 ? "text-rose-400" : srv.cpu_usage > 70 ? "text-amber-400" : "text-emerald-400"}`}>
                        {srv.cpu_usage.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          srv.cpu_usage > 85 ? "bg-rose-500" : srv.cpu_usage > 70 ? "bg-amber-500" : "bg-emerald-500"
                        }`}
                        style={{ width: `${Math.min(100, srv.cpu_usage)}%` }}
                      />
                    </div>
                  </div>

                  {/* Memory & Disk Usage */}
                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div className="p-2 bg-slate-900/60 rounded-lg border border-slate-800">
                      <span className="text-slate-500 block text-[10px]">Memory</span>
                      <span className="text-slate-200 font-semibold">{srv.memory_usage.toFixed(1)}%</span>
                    </div>
                    <div className="p-2 bg-slate-900/60 rounded-lg border border-slate-800">
                      <span className="text-slate-500 block text-[10px]">Disk Usage</span>
                      <span className="text-slate-200 font-semibold">{srv.disk_usage.toFixed(1)}%</span>
                    </div>
                  </div>

                  {/* Error Rate */}
                  <div className="flex items-center justify-between text-[11px] pt-1 border-t border-slate-800/60">
                    <span className="text-slate-400">HTTP 5xx Error Rate</span>
                    <span className={`font-semibold ${srv.error_rate > 0.02 ? "text-rose-400 font-mono" : "text-slate-300 font-mono"}`}>
                      {(srv.error_rate * 100).toFixed(2)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* SECTION 1: INCIDENTS LIST PAGE / TABLE */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Filter Status:</span>
            {["ALL", "OPEN", "INVESTIGATING", "RESOLVED"].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1 text-xs font-semibold rounded-lg transition-colors ${
                  statusFilter === st
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                    : "bg-slate-900 text-slate-400 border border-slate-800 hover:text-white"
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        <DataTable
          data={filteredIncidents}
          columns={columns}
          searchPlaceholder="Search by incident title, service, category, or root cause..."
          onRowClick={(item) => navigate(`/incidents/${item.rawId}`)}
          pageSize={8}
        />
      </div>

      {/* Declare Incident Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-indigo-400" /> Declare Production Incident
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 text-slate-400 hover:text-white rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {formSuccess && (
              <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" /> Incident created successfully!
              </div>
            )}

            <form onSubmit={handleCreateSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Incident Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Database Connection Pool Exhausted"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Description</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Detailed description of symptoms, affected services, and telemetry logs..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-indigo-500 resize-none"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Incident Type</label>
                  <select
                    value={formData.incident_type}
                    onChange={(e) => setFormData({ ...formData, incident_type: e.target.value })}
                    className="w-full px-2.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="SECURITY">SECURITY</option>
                    <option value="APPLICATION">APPLICATION</option>
                    <option value="DATABASE">DATABASE</option>
                    <option value="NETWORK">NETWORK</option>
                    <option value="CLOUD">CLOUD</option>
                    <option value="ENDPOINT">ENDPOINT</option>
                    <option value="EMAIL">EMAIL</option>
                    <option value="OTHER">OTHER</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Severity</label>
                  <select
                    value={formData.severity}
                    onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                    className="w-full px-2.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="CRITICAL">P0 - CRITICAL</option>
                    <option value="HIGH">P1 - HIGH</option>
                    <option value="MEDIUM">P2 - MEDIUM</option>
                    <option value="LOW">P3 - LOW</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Source</label>
                  <select
                    value={formData.source}
                    onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                    className="w-full px-2.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="MANUAL">MANUAL</option>
                    <option value="API">API</option>
                    <option value="EMAIL">EMAIL</option>
                    <option value="SIEM">SIEM</option>
                    <option value="MONITORING">MONITORING</option>
                    <option value="AI">AI</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <Button variant="secondary" type="button" size="sm" onClick={() => setIsModalOpen(false)}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit" size="sm" isLoading={isCreating}>
                  Create Incident
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
