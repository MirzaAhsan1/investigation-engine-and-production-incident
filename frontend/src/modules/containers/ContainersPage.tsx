import { useState, useMemo, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Boxes,
  RefreshCw,
  Search,
  Server,
  AlertTriangle,
  ShieldAlert,
  Terminal,
  ArrowRight,
  Clock,
  CheckCircle2,
  Radio,
} from "lucide-react";
import { useGetLogsQuery } from "../../api/logsApi";
import { Skeleton } from "../../components/ui/Skeleton";

export interface ContainerInfo {
  name: string;
  applicationName: string;
  host: string;
  totalLogs: number;
  errorCount: number;
  warnCount: number;
  lastActive: string;
  status: "HEALTHY" | "WARNING" | "CRITICAL";
}

export interface LiveWsLogPayload {
  timestamp?: string;
  level?: string;
  message?: string;
  container_name?: string;
  application_name?: string;
  host?: string;
}

export default function ContainersPage() {
  const navigate = useNavigate();
  const { data: logs, isLoading, isFetching, error, refetch } = useGetLogsQuery(undefined, {
    pollingInterval: 5000,
  });

  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<"ALL" | "HEALTHY" | "WARNING" | "CRITICAL">("ALL");

  // WebSocket Live Streaming logs state for instant runtime discovery
  const [wsLogs, setWsLogs] = useState<LiveWsLogPayload[]>([]);
  const [wsConnected, setWsConnected] = useState<boolean>(false);

  useEffect(() => {
    let wsUrl = "";
    const envApiUrl = import.meta.env.VITE_API_BASE_URL;
    if (envApiUrl) {
      const urlObj = new URL(envApiUrl, window.location.origin);
      const wsProtocol = urlObj.protocol === "https:" ? "wss:" : "ws:";
      wsUrl = `${wsProtocol}//${urlObj.host}/api/ws/logs`;
    } else {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.host;
      wsUrl = `${protocol}//${host}/api/ws/logs`;
    }

    let socket: WebSocket | null = new WebSocket(wsUrl);

    socket.onopen = () => {
      setWsConnected(true);
    };

    socket.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setWsLogs((prev) => [parsed, ...prev].slice(0, 500));
      } catch (err) {
        console.error("Failed to parse websocket log on Containers page:", err);
      }
    };

    socket.onclose = () => {
      setWsConnected(false);
    };

    socket.onerror = () => {
      setWsConnected(false);
    };

    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, []);

  // Process stored DB logs + Live WebSocket logs into real-time active container objects
  const containers = useMemo(() => {
    const map = new Map<string, ContainerInfo>();

    // 1. Process stored DB logs
    if (logs && logs.length > 0) {
      logs.forEach((log) => {
        const containerName = log.container_name || log.application_name || "app-service";
        const appName = log.application_name || "Unknown App";
        const hostName = log.host || log.server_name || "cluster-node";

        const existing = map.get(containerName);

        if (!existing) {
          const isErr = log.level === "ERROR";
          const isWarn = log.level === "WARN";
          map.set(containerName, {
            name: containerName,
            applicationName: appName,
            host: hostName,
            totalLogs: 1,
            errorCount: isErr ? 1 : 0,
            warnCount: isWarn ? 1 : 0,
            lastActive: log.timestamp,
            status: isErr ? "CRITICAL" : isWarn ? "WARNING" : "HEALTHY",
          });
        } else {
          existing.totalLogs += 1;
          if (log.level === "ERROR") existing.errorCount += 1;
          if (log.level === "WARN") existing.warnCount += 1;

          if (new Date(log.timestamp) > new Date(existing.lastActive)) {
            existing.lastActive = log.timestamp;
          }

          if (existing.errorCount > 0) {
            existing.status = "CRITICAL";
          } else if (existing.warnCount > 0 && existing.status !== "CRITICAL") {
            existing.status = "WARNING";
          }
        }
      });
    }

    // 2. Process real-time streaming WebSocket logs (non-DB)
    wsLogs.forEach((wsLog) => {
      const containerName = wsLog.container_name || wsLog.application_name || "app-service";
      const appName = wsLog.application_name || "Unknown App";
      const hostName = wsLog.host || "cluster-node";
      const timestamp = wsLog.timestamp || new Date().toISOString();
      const level = (wsLog.level || "INFO").toUpperCase();

      const existing = map.get(containerName);

      if (!existing) {
        const isErr = level === "ERROR";
        const isWarn = level === "WARN";
        map.set(containerName, {
          name: containerName,
          applicationName: appName,
          host: hostName,
          totalLogs: 1,
          errorCount: isErr ? 1 : 0,
          warnCount: isWarn ? 1 : 0,
          lastActive: timestamp,
          status: isErr ? "CRITICAL" : isWarn ? "WARNING" : "HEALTHY",
        });
      } else {
        existing.totalLogs += 1;
        if (level === "ERROR") existing.errorCount += 1;
        if (level === "WARN") existing.warnCount += 1;

        if (new Date(timestamp) > new Date(existing.lastActive)) {
          existing.lastActive = timestamp;
        }

        if (existing.errorCount > 0) {
          existing.status = "CRITICAL";
        } else if (existing.warnCount > 0 && existing.status !== "CRITICAL") {
          existing.status = "WARNING";
        }
      }
    });

    return Array.from(map.values()).sort((a, b) => new Date(b.lastActive).getTime() - new Date(a.lastActive).getTime());
  }, [logs, wsLogs]);

  // Filtered containers list
  const filteredContainers = useMemo(() => {
    const term = searchTerm.toLowerCase().trim();
    return containers.filter((c) => {
      const matchesSearch =
        !term ||
        c.name.toLowerCase().includes(term) ||
        c.applicationName.toLowerCase().includes(term) ||
        c.host.toLowerCase().includes(term);

      const matchesStatus = statusFilter === "ALL" || c.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [containers, searchTerm, statusFilter]);

  // General fleet stats
  const fleetStats = useMemo(() => {
    const totalContainers = containers.length;
    const criticalCount = containers.filter((c) => c.status === "CRITICAL").length;
    const warningCount = containers.filter((c) => c.status === "WARNING").length;
    const healthyCount = containers.filter((c) => c.status === "HEALTHY").length;
    const totalLogsCount = logs ? logs.length : 0;

    return { totalContainers, criticalCount, warningCount, healthyCount, totalLogsCount };
  }, [containers, logs]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Boxes className="w-5 h-5" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">Active Containers</h1>
            <span className="flex items-center gap-1.5 text-[11px] bg-emerald-500/10 text-emerald-400 font-medium px-2.5 py-0.5 rounded-full border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Runtime Sync (5s)
            </span>
            <span
              className={`flex items-center gap-1.5 text-[11px] font-medium px-2.5 py-0.5 rounded-full border ${wsConnected
                ? "bg-indigo-500/10 text-indigo-400 border-indigo-500/20"
                : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                }`}
            >
              <Radio className="w-3 h-3 animate-pulse" />
              {wsConnected ? "WebSocket Live" : "WS Offline"}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time breakdown of active fleet containers discovered from live system logs and app telemetry
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-200 hover:text-white hover:bg-slate-800 transition-all duration-150 shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-indigo-400 ${isFetching ? "animate-spin" : ""}`} />
            <span>{isFetching ? "Syncing..." : "Refresh"}</span>
          </button>
        </div>
      </div>

      {/* Fleet Stats Overview */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Active Containers</span>
            <Boxes className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-xl font-bold text-white">{fleetStats.totalContainers}</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Healthy Fleet</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-xl font-bold text-emerald-400">{fleetStats.healthyCount}</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Warnings</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-xl font-bold text-amber-400">{fleetStats.warningCount}</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Critical Issues</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-xl font-bold text-rose-400">{fleetStats.criticalCount}</p>
        </div>
      </div>

      {/* Filter and Search controls */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search by container name, application, host..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-950/80 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50"
          />
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400 font-medium">Filter Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as any)}
            className="bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-indigo-500/50"
          >
            <option value="ALL">All Statuses</option>
            <option value="HEALTHY">Healthy</option>
            <option value="WARNING">Warning</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
      </div>

      {/* Containers Grid View */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} height="h-44" />
          ))}
        </div>
      ) : error ? (
        <div className="p-8 bg-rose-500/5 border border-rose-500/20 rounded-xl text-center space-y-3">
          <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto" />
          <h3 className="text-sm font-bold text-rose-300">Failed to Fetch Containers Data</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Unable to stream log data to calculate runtime container status.
          </p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded-lg hover:bg-rose-500/30 transition-colors"
          >
            Retry Sync
          </button>
        </div>
      ) : filteredContainers.length === 0 ? (
        <div className="p-12 bg-slate-900/40 border border-slate-800 rounded-xl text-center space-y-3">
          <Boxes className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-sm font-semibold text-slate-300">No Containers Found</h3>
          <p className="text-xs text-slate-500">
            {containers.length > 0
              ? "No containers match your search or status filter."
              : "No active container log events recorded in the system yet."}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredContainers.map((container) => {
            const statusBadge =
              container.status === "CRITICAL"
                ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
                : container.status === "WARNING"
                  ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                  : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";

            return (
              <div
                key={container.name}
                onClick={() => navigate(`/containers/${encodeURIComponent(container.name)}`)}
                className="group p-5 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-indigo-500/40 hover:bg-slate-900/90 transition-all duration-200 cursor-pointer shadow-lg flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex items-center gap-2.5">
                      <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 group-hover:scale-105 transition-transform">
                        <Boxes className="w-4 h-4" />
                      </div>
                      <div>
                        <h3 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors font-mono">
                          {container.name}
                        </h3>
                        <span className="text-[11px] text-slate-400">{container.applicationName}</span>
                      </div>
                    </div>

                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${statusBadge}`}
                    >
                      {container.status}
                    </span>
                  </div>

                  {/* Details stats */}
                  <div className="grid grid-cols-3 gap-2 py-3 border-y border-slate-800/80 my-3 text-center">
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase font-semibold block">Logs</span>
                      <span className="text-sm font-bold text-slate-200">{container.totalLogs}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase font-semibold block">Errors</span>
                      <span
                        className={`text-sm font-bold ${container.errorCount > 0 ? "text-rose-400" : "text-slate-400"
                          }`}
                      >
                        {container.errorCount}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase font-semibold block">Warnings</span>
                      <span
                        className={`text-sm font-bold ${container.warnCount > 0 ? "text-amber-400" : "text-slate-400"
                          }`}
                      >
                        {container.warnCount}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-1.5 text-xs text-slate-400">
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-1.5 text-slate-500">
                        <Server className="w-3 h-3" /> Host:
                      </span>
                      <span className="font-mono text-slate-300 text-[11px]">{container.host}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-1.5 text-slate-500">
                        <Clock className="w-3 h-3" /> Last Active:
                      </span>
                      <span className="font-mono text-slate-400 text-[11px]">
                        {new Date(container.lastActive).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                          second: "2-digit",
                        })}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-indigo-400 group-hover:text-indigo-300 font-semibold">
                  <span className="flex items-center gap-1.5">
                    <Terminal className="w-3.5 h-3.5" /> View Container Logs
                  </span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
