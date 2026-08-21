import {
  AlertTriangle,
  Activity,
  Sparkles,
  TrendingDown,
  Clock,
  Server,
  Zap,
  ShieldAlert,
  Brain,
} from "lucide-react";
import { MetricCard } from "../../components/ui/MetricCard";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { useNavigate } from "react-router-dom";
import { useGetIncidentsQuery, type BackendIncident } from "../../api/incidentsApi";

const incidentTrend = [
  { time: "Mon", count: 4, resolved: 3 },
  { time: "Tue", count: 7, resolved: 5 },
  { time: "Wed", count: 3, resolved: 3 },
  { time: "Thu", count: 9, resolved: 6 },
  { time: "Fri", count: 5, resolved: 5 },
  { time: "Sat", count: 2, resolved: 2 },
  { time: "Sun", count: 6, resolved: 4 },
];

const recentIncidents = [
  { id: "INC-1042", title: "API Gateway High Latency – prod", severity: "P1" as const, status: "INVESTIGATING" as const, service: "api-gateway", time: "12 min ago" },
  { id: "INC-1041", title: "Database Connection Pool Exhausted", severity: "P0" as const, status: "OPEN" as const, service: "postgres-primary", time: "31 min ago" },
  { id: "INC-1040", title: "Payment Service 5xx Spike", severity: "P1" as const, status: "MITIGATED" as const, service: "payment-svc", time: "2h 14m ago" },
  { id: "INC-1039", title: "Redis Cache Miss Rate > 60%", severity: "P2" as const, status: "RESOLVED" as const, service: "redis-cluster", time: "5h ago" },
];

const aiRecommendations = [
  { id: "REC-089", title: "Scale payment-svc pods to 8 replicas", confidence: 94, risk: "LOW" as const, incident: "INC-1040" },
  { id: "REC-088", title: "Flush Redis cache and restart replica set", confidence: 88, risk: "MEDIUM" as const, incident: "INC-1039" },
  { id: "REC-087", title: "Rollback api-gateway to v2.3.1", confidence: 97, risk: "LOW" as const, incident: "INC-1042" },
];

const services = [
  { name: "api-gateway", status: "DEGRADED" as const, uptime: 99.1 },
  { name: "auth-service", status: "OPERATIONAL" as const, uptime: 99.99 },
  { name: "payment-svc", status: "OPERATIONAL" as const, uptime: 99.7 },
  { name: "postgres-primary", status: "OUTAGE" as const, uptime: 97.2 },
  { name: "redis-cluster", status: "OPERATIONAL" as const, uptime: 99.95 },
];

const statusColors: Record<string, string> = {
  OPERATIONAL: "bg-emerald-400",
  DEGRADED: "bg-amber-400",
  OUTAGE: "bg-rose-400 animate-pulse",
};

export default function DashboardPage() {
  const navigate = useNavigate();
  const { data: backendIncidents } = useGetIncidentsQuery();

  // Compute live counts (fallback to static if API unavailable)
  const activeBackendIncidents = (backendIncidents || []).filter(
    (i: BackendIncident) => i.status === "OPEN" || i.status === "INVESTIGATING"
  );
  const activeCount = backendIncidents ? activeBackendIncidents.length : 3;

  // Severity breakdown from live data
  const p0Count = backendIncidents
    ? activeBackendIncidents.filter((i: BackendIncident) => i.severity === "CRITICAL").length
    : 1;
  const p1Count = backendIncidents
    ? activeBackendIncidents.filter((i: BackendIncident) => i.severity === "HIGH").length
    : 2;

  // Merge live incidents into the recent list (live first, then static fallback)
  const liveRecentIncidents: typeof recentIncidents = (backendIncidents || []).slice(0, 4).map((b: BackendIncident) => {
    const severityMap: Record<string, string> = { CRITICAL: "P0", HIGH: "P1", MEDIUM: "P2", LOW: "P3" };
    return {
      id: b.id.slice(0, 8),
      title: b.title,
      severity: (severityMap[b.severity] || b.severity) as any,
      status: b.status as any,
      service: b.incident_type.toLowerCase() + "-svc",
      time: new Date(b.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
  });
  const mergedRecentIncidents = liveRecentIncidents.length > 0
    ? [...liveRecentIncidents, ...recentIncidents.slice(0, Math.max(0, 4 - liveRecentIncidents.length))]
    : recentIncidents;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-50 tracking-tight">Command Center</h1>
          <p className="text-sm text-slate-400 mt-0.5">Real-time AI incident monitoring and response overview</p>
        </div>
        <div className="flex items-center gap-2.5">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-violet-500/10 border border-violet-500/20 text-xs font-medium text-violet-300">
            <Brain className="w-3.5 h-3.5 animate-pulse" />
            <span>AI Agent Active</span>
          </div>
          <Button variant="primary" size="sm" leftIcon={<AlertTriangle className="w-3.5 h-3.5" />}
            onClick={() => navigate("/incidents")}>
            New Incident
          </Button>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Incidents"
          value={String(activeCount)}
          change={backendIncidents ? `${activeCount} live from API` : "+1 vs yesterday"}
          changeType="decrease"
          subtitle={`P0: ${p0Count} · P1: ${p1Count}`}
          icon={<AlertTriangle className="w-5 h-5 text-rose-400" />}
          statusColor="rose"
        />
        <MetricCard
          title="Avg MTTR"
          value="24m"
          change="-8m this week"
          changeType="increase"
          subtitle="vs 32m last week"
          icon={<Clock className="w-5 h-5 text-amber-400" />}
          statusColor="amber"
        />
        <MetricCard
          title="AI Accuracy"
          value="94.7%"
          change="+1.2% vs last month"
          changeType="increase"
          subtitle="Root cause detection"
          icon={<Sparkles className="w-5 h-5 text-violet-400" />}
          statusColor="indigo"
        />
        <MetricCard
          title="System Availability"
          value="99.91%"
          change="-0.05% this week"
          changeType="decrease"
          subtitle="Across 5 services"
          icon={<Activity className="w-5 h-5 text-emerald-400" />}
          statusColor="emerald"
        />
      </div>

      {/* Incident Trend Chart + Service Status */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        <div className="xl:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>
                <TrendingDown className="w-4 h-4 text-indigo-400" />
                Incident Trend – Last 7 Days
              </CardTitle>
              <span className="text-xs text-slate-400">Total vs Resolved</span>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={incidentTrend} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                  <defs>
                    <linearGradient id="countGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="resolvedGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                  <XAxis dataKey="time" tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={false} tickLine={false} />
                  <Tooltip
                    contentStyle={{ background: "#111827", border: "1px solid #1f2937", borderRadius: 8, fontSize: 12 }}
                    labelStyle={{ color: "#f9fafb" }}
                  />
                  <Area type="monotone" dataKey="count" name="Total" stroke="#6366f1" fill="url(#countGrad)" strokeWidth={2} dot={false} />
                  <Area type="monotone" dataKey="resolved" name="Resolved" stroke="#10b981" fill="url(#resolvedGrad)" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>
              <Server className="w-4 h-4 text-indigo-400" />
              Service Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {services.map((svc) => (
                <div key={svc.name} className="flex items-center justify-between py-1.5 border-b border-slate-800/50 last:border-0">
                  <div className="flex items-center gap-2.5">
                    <div className={`w-2 h-2 rounded-full ${statusColors[svc.status]}`} />
                    <span className="text-xs text-slate-200 font-mono font-medium">{svc.name}</span>
                  </div>
                  <div className="text-right">
                    <Badge variant="status" status={svc.status as any}>
                      {svc.status}
                    </Badge>
                    <p className="text-[10px] text-slate-500 mt-0.5">{svc.uptime}% uptime</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Incidents + AI Recommendations */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <Card>
          <CardHeader>
            <CardTitle>
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              Recent Incidents
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={() => navigate("/incidents")}>
              View all
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {mergedRecentIncidents.map((inc) => (
                <div
                  key={inc.id}
                  className="flex items-start gap-3 p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 hover:bg-slate-800/40 transition-colors cursor-pointer group"
                  onClick={() => navigate(`/incidents/${inc.id}`)}
                >
                  <div className="flex flex-col items-center gap-1.5 flex-shrink-0 pt-0.5">
                    <Badge variant="severity" severity={inc.severity as any}>{inc.severity}</Badge>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-semibold text-slate-100 group-hover:text-indigo-300 transition-colors truncate">{inc.title}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] text-slate-500 font-mono">{inc.id}</span>
                      <span className="text-[10px] text-slate-600">·</span>
                      <span className="text-[10px] text-slate-500">{inc.time}</span>
                    </div>
                  </div>
                  <Badge variant="status" status={inc.status as any}>{inc.status}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card variant="glow">
          <CardHeader>
            <CardTitle>
              <Zap className="w-4 h-4 text-violet-400" />
              AI Recommendations
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={() => navigate("/recommendations")}>
              View all
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {aiRecommendations.map((rec) => (
                <div key={rec.id} className="p-3 rounded-xl bg-slate-950/80 border border-violet-500/10 hover:border-violet-500/30 transition-colors">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-slate-100 truncate">{rec.title}</p>
                      <p className="text-[10px] text-slate-500 font-mono mt-0.5">{rec.incident}</p>
                    </div>
                    <Badge variant="severity" severity={rec.risk as any}>{rec.risk}</Badge>
                  </div>
                  <div className="mt-2 flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <div className="h-1.5 w-24 bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full"
                          style={{ width: `${rec.confidence}%` }}
                        />
                      </div>
                      <span className="text-[10px] font-semibold text-violet-300">{rec.confidence}%</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Button variant="ghost" size="sm" className="py-0.5 px-2 text-[10px] text-emerald-400 hover:bg-emerald-500/10">
                        Approve
                      </Button>
                      <Button variant="ghost" size="sm" className="py-0.5 px-2 text-[10px] text-rose-400 hover:bg-rose-500/10">
                        Reject
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
