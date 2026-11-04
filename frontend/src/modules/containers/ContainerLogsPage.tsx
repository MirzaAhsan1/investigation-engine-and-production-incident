import { useState, useMemo, useEffect, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft,
  Boxes,
  RefreshCw,
  Search,
  Filter,
  Layers,
  Server,
  ShieldAlert,
  Clock,
  Terminal,
  AlertTriangle,
  X,
  Maximize2,
  Radio,
  Trash2,
  Pause,
  Play,
} from "lucide-react";
import { useGetLogsQuery, type LogItem } from "../../api/logsApi";
import { useGetApplicationsQuery } from "../../api/applicationsApi";
import { Skeleton } from "../../components/ui/Skeleton";

export interface LiveWsLog {
  id: string;
  timestamp: string;
  level: string;
  message: string;
  container_name?: string;
  host?: string;
}

const levelStyles: Record<string, { bg: string; text: string; border: string }> = {
  ERROR: { bg: "bg-rose-500/10", text: "text-rose-400", border: "border-rose-500/20" },
  WARN: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/20" },
  INFO: { bg: "bg-sky-500/10", text: "text-sky-400", border: "border-sky-500/20" },
  DEBUG: { bg: "bg-slate-500/10", text: "text-slate-400", border: "border-slate-500/20" },
};

const statusStyles: Record<string, { bg: string; text: string; border: string }> = {
  OPEN: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/20" },
  PENDING: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/20" },
  PROCESSING: { bg: "bg-indigo-500/10", text: "text-indigo-400", border: "border-indigo-500/20" },
  IN_PROGRESS: { bg: "bg-indigo-500/10", text: "text-indigo-400", border: "border-indigo-500/20" },
  RESOLVED: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/20" },
  COMPLETED: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/20" },
  FAILED: { bg: "bg-rose-500/10", text: "text-rose-400", border: "border-rose-500/20" },
  CLOSED: { bg: "bg-slate-500/10", text: "text-slate-400", border: "border-slate-500/20" },
};

export default function ContainerLogsPage() {
  const { containerName } = useParams<{ containerName: string }>();
  const decodedContainerName = containerName ? decodeURIComponent(containerName) : "";

  // 1. Stable metadata check (applications)
  const { data: applications } = useGetApplicationsQuery(undefined, {
    pollingInterval: 30000,
  });

  const currentApp = useMemo(() => {
    if (!applications) return null;
    return applications.find(
      (app) =>
        app.container_name === decodedContainerName ||
        app.name === decodedContainerName ||
        app.id === decodedContainerName ||
        (app.resource_uuid && app.resource_uuid === decodedContainerName)
    );
  }, [applications, decodedContainerName]);

  // Keep a live ref to currentApp so WebSocket callbacks always use latest metadata without stale closures
  const currentAppRef = useRef(currentApp);
  useEffect(() => {
    currentAppRef.current = currentApp;
  }, [currentApp]);

  // Clear live logs when container selection changes
  useEffect(() => {
    setLiveLogs([]);
  }, [decodedContainerName]);

  // 2. Poll DB logs for this container
  const { data: logs, isLoading, isFetching, error, refetch } = useGetLogsQuery(
    decodedContainerName ? { container_name: decodedContainerName } : undefined,
    { pollingInterval: 5000 }
  );

  const [searchQuery, setSearchQuery] = useState("");
  const [levelFilter, setLevelFilter] = useState<string>("ALL");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [selectedLog, setSelectedLog] = useState<LogItem | null>(null);

  // Live WebSocket Logs state for this specific container
  const [liveLogs, setLiveLogs] = useState<LiveWsLog[]>([]);
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const liveLogsEndRef = useRef<HTMLDivElement | null>(null);

  // Persistent stats to prevent metrics from resetting to 0 when DB logs are empty
  const [lastKnownStats, setLastKnownStats] = useState<{
    total: number;
    errors: number;
    warnings: number;
    host: string;
    status: "HEALTHY" | "WARNING" | "CRITICAL";
  }>({
    total: 0,
    errors: 0,
    warnings: 0,
    host: "cluster-node",
    status: "HEALTHY",
  });

  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
    let isComponentMounted = true;

    const connectWebSocket = () => {
      let wsUrl = "";
      const envApiUrl = import.meta.env.VITE_API_BASE_URL;
      if (envApiUrl && (envApiUrl.startsWith("http://") || envApiUrl.startsWith("https://"))) {
        try {
          const urlObj = new URL(envApiUrl);
          const wsProtocol = urlObj.protocol === "https:" ? "wss:" : "ws:";
          wsUrl = `${wsProtocol}//${urlObj.host}/api/ws/logs`;
        } catch {
          const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
          wsUrl = `${protocol}//${window.location.host}/api/ws/logs`;
        }
      } else {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const host = window.location.host;
        wsUrl = `${protocol}//${host}/api/ws/logs`;
      }

      try {
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
          if (isComponentMounted) {
            setWsConnected(true);
          }
        };

        socket.onmessage = (event) => {
          if (!isComponentMounted || isPaused) return;
          try {
            const parsed = JSON.parse(event.data);
            console.log("[WebSocket Received on ContainerLogsPage]:", parsed);

            // Handle WebSocket control/heartbeat messages
            if (parsed.type === "connected") {
              setWsConnected(true);
              return;
            }
            if (parsed.type === "ping") {
              if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send("pong");
              }
              return;
            }
            if (parsed.type === "pong") {
              return;
            }

            // Target identifiers associated with this container detail page
            const targetNames = [
              decodedContainerName,
              currentAppRef.current?.container_name,
              currentAppRef.current?.name,
              currentAppRef.current?.resource_uuid,
            ]
              .filter(Boolean)
              .map((n) => n!.trim().toLowerCase());

            const logContainer = (parsed.container_name || "").trim().toLowerCase();
            const logApp = (parsed.application_name || "").trim().toLowerCase();

            // Token overlap matching for container name variations
            const targetTokens = targetNames
              .flatMap((name) => name.split(/[-_.]/))
              .filter((t) => t.length > 2);

            const logTokens = `${logContainer} ${logApp}`
              .split(/[-_.\s]/)
              .filter((t) => t.length > 2);

            const isForThisContainer =
              !decodedContainerName ||
              targetNames.length === 0 ||
              targetNames.some(
                (target) =>
                  (logContainer && (logContainer === target || logContainer.includes(target) || target.includes(logContainer))) ||
                  (logApp && (logApp === target || logApp.includes(target) || target.includes(logApp)))
              ) ||
              (targetTokens.length > 0 && targetTokens.some((token) => logTokens.includes(token)));

            if (!isForThisContainer) return;

            const newLog: LiveWsLog = {
              id: Math.random().toString(36).substring(2, 9),
              timestamp: parsed.timestamp || new Date().toISOString(),
              level: parsed.level || "INFO",
              message: parsed.message || "",
              container_name: parsed.container_name || decodedContainerName,
              host: parsed.host,
            };
            setLiveLogs((prev) => [newLog, ...prev].slice(0, 200));
          } catch (err) {
            console.error("Failed to parse websocket log:", err);
          }
        };

        socket.onclose = () => {
          if (!isComponentMounted) return;
          setWsConnected(false);
          // Auto reconnect after 3 seconds
          reconnectTimeout = setTimeout(() => {
            if (isComponentMounted) {
              connectWebSocket();
            }
          }, 3000);
        };

        socket.onerror = () => {
          if (isComponentMounted) {
            setWsConnected(false);
          }
        };
      } catch (err) {
        console.error("WebSocket connection error:", err);
        if (isComponentMounted) {
          setWsConnected(false);
          reconnectTimeout = setTimeout(() => {
            if (isComponentMounted) {
              connectWebSocket();
            }
          }, 5000);
        }
      }
    };

    connectWebSocket();

    return () => {
      isComponentMounted = false;
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (socket) {
        socket.close();
      }
    };
  }, [isPaused, decodedContainerName]);

  // Update persistent stats state
  useEffect(() => {
    if (!logs) return;

    const containerLogs = logs.filter(
      (l) =>
        !decodedContainerName ||
        l.container_name === decodedContainerName ||
        (!l.container_name && l.application_name === decodedContainerName)
    );

    if (containerLogs.length > 0 || liveLogs.length > 0) {
      const dbErrors = containerLogs.filter((l) => l.level === "ERROR").length;
      const dbWarnings = containerLogs.filter((l) => l.level === "WARN").length;

      const liveErrors = liveLogs.filter((l) => l.level === "ERROR").length;
      const liveWarnings = liveLogs.filter((l) => l.level === "WARN").length;

      const totalErrors = dbErrors + liveErrors;
      const totalWarnings = dbWarnings + liveWarnings;
      const totalEvents = containerLogs.length + liveLogs.length;

      const host = containerLogs[0]?.host || containerLogs[0]?.server_name || liveLogs[0]?.host || "cluster-node";

      let containerStatus: "HEALTHY" | "WARNING" | "CRITICAL" = "HEALTHY";
      if (totalErrors > 0) {
        containerStatus = "CRITICAL";
      } else if (totalWarnings > 0) {
        containerStatus = "WARNING";
      }

      setLastKnownStats({
        total: totalEvents,
        errors: totalErrors,
        warnings: totalWarnings,
        host,
        status: containerStatus,
      });
    }
  }, [logs, liveLogs, decodedContainerName]);

  // Filter logs for this specific container
  const filteredLogs = useMemo(() => {
    if (!logs) return [];
    const term = searchQuery.toLowerCase().trim();

    return logs.filter((log) => {
      // Safety check in case backend return all logs or app matching
      const isForContainer =
        !decodedContainerName ||
        log.container_name === decodedContainerName ||
        (!log.container_name && log.application_name === decodedContainerName);

      if (!isForContainer) return false;

      const matchesSearch =
        !term ||
        (log.message && log.message.toLowerCase().includes(term)) ||
        (log.host && log.host.toLowerCase().includes(term)) ||
        (log.correlation_group_id && log.correlation_group_id.toLowerCase().includes(term));

      const matchesLevel = levelFilter === "ALL" || log.level === levelFilter;
      const matchesStatus = statusFilter === "ALL" || log.status === statusFilter;

      return matchesSearch && matchesLevel && matchesStatus;
    });
  }, [logs, decodedContainerName, searchQuery, levelFilter, statusFilter]);

  const stats = useMemo(() => {
    const displayHost = lastKnownStats.host !== "cluster-node" 
      ? lastKnownStats.host 
      : "cluster-node";

    return {
      total: lastKnownStats.total,
      errors: lastKnownStats.errors,
      warnings: lastKnownStats.warnings,
      host: displayHost,
      status: lastKnownStats.status,
    };
  }, [lastKnownStats]);

  return (
    <div className="space-y-6">
      {/* Navigation & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Link
            to="/containers"
            className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 font-semibold mb-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Containers
          </Link>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Boxes className="w-5 h-5" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight font-mono">
              {currentApp ? `${currentApp.name} (${decodedContainerName})` : (decodedContainerName || "Container Logs")}
            </h1>
            <span
              className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                stats.status === "CRITICAL"
                  ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
                  : stats.status === "WARNING"
                  ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                  : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
              }`}
            >
              Status: {stats.status}
            </span>
            <span className="flex items-center gap-1.5 text-[11px] bg-emerald-500/10 text-emerald-400 font-medium px-2.5 py-0.5 rounded-full border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Live Stream (5s)
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Displaying real-time runtime log events isolated to container <code className="text-indigo-300 font-mono">{decodedContainerName}</code>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-200 hover:text-white hover:bg-slate-800 transition-all duration-150 shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-indigo-400 ${isFetching ? "animate-spin" : ""}`} />
            <span>{isFetching ? "Refreshing..." : "Refresh Logs"}</span>
          </button>
        </div>
      </div>

      {/* Container Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Container Status</span>
            <Boxes className="w-4 h-4 text-indigo-400" />
          </div>
          <p
            className={`text-lg font-extrabold ${
              stats.status === "CRITICAL"
                ? "text-rose-400"
                : stats.status === "WARNING"
                ? "text-amber-400"
                : "text-emerald-400"
            }`}
          >
            {stats.status}
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Total Log Events</span>
            <Layers className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-xl font-bold text-white">{stats.total}</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Errors</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-xl font-bold text-rose-400">{stats.errors}</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Warnings</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-xl font-bold text-amber-400">{stats.warnings}</p>
        </div>
      </div>

      {/* Live Stream Console (WebSocket - Runtime Non-DB logs) */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-xl backdrop-blur-md space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Radio className="w-4 h-4 animate-pulse text-indigo-400" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-tight">
                Live WebSocket Stream Console (Runtime Logs)
              </h2>
              <p className="text-[11px] text-slate-400">
                Non-DB live log stream isolated to <code className="text-indigo-300 font-mono">{decodedContainerName}</code>
              </p>
            </div>
            <span
              className={`ml-2 flex items-center gap-1.5 text-[10px] font-medium px-2 py-0.5 rounded-full border ${
                wsConnected
                  ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                  : "bg-rose-500/10 text-rose-400 border-rose-500/20"
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${wsConnected ? "bg-emerald-400 animate-ping" : "bg-rose-400"}`} />
              {wsConnected ? "Connected" : "Disconnected"}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsPaused(!isPaused)}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
            >
              {isPaused ? <Play className="w-3 h-3 text-emerald-400" /> : <Pause className="w-3 h-3 text-amber-400" />}
              <span>{isPaused ? "Resume" : "Pause"}</span>
            </button>
            <button
              onClick={() => setLiveLogs([])}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-medium text-slate-400 hover:text-rose-300 hover:bg-slate-800 transition-colors"
            >
              <Trash2 className="w-3 h-3" />
              <span>Clear</span>
            </button>
          </div>
        </div>

        <div className="font-mono text-[11px] bg-slate-950/90 rounded-lg border border-slate-800/80 p-3 space-y-1.5 max-h-[300px] overflow-y-auto">
          {liveLogs.length === 0 ? (
            <div className="h-24 flex items-center justify-center text-slate-600 text-xs italic">
              Listening for real-time WebSocket logs for container [{decodedContainerName}]...
            </div>
          ) : (
            liveLogs.map((log) => {
              const style = levelStyles[log.level] || levelStyles.INFO;
              return (
                <div key={log.id} className="flex items-start gap-2 leading-relaxed border-b border-slate-900/60 pb-1 hover:bg-slate-900/30 rounded px-1 transition-colors">
                  <span className="text-slate-500 shrink-0">
                    {new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                  <span className={`px-1.5 py-0.2 text-[9px] rounded font-bold uppercase border ${style.bg} ${style.text} ${style.border}`}>
                    {log.level}
                  </span>
                  {log.container_name && (
                    <span className="text-indigo-400 font-semibold shrink-0">[{log.container_name}]</span>
                  )}
                  <span className="text-slate-300 break-all">{log.message}</span>
                </div>
              );
            })
          )}
          <div ref={liveLogsEndRef} />
        </div>
      </div>

      <div className="pt-2">
        <h2 className="text-sm font-bold text-white tracking-tight mb-3 flex items-center gap-2">
          <Terminal className="w-4 h-4 text-indigo-400" />
          <span>Stored Log Events Database (`log_events`)</span>
        </h2>
      </div>

      {/* Filter and Search controls */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search container logs by message or correlation ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-950/80 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs text-slate-400 font-medium">Level:</span>
            <select
              value={levelFilter}
              onChange={(e) => setLevelFilter(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-indigo-500/50"
            >
              <option value="ALL">All Levels</option>
              <option value="ERROR">ERROR</option>
              <option value="WARN">WARN</option>
              <option value="INFO">INFO</option>
              <option value="DEBUG">DEBUG</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-medium">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-indigo-500/50"
            >
              <option value="ALL">All Statuses</option>
              <option value="PENDING">PENDING</option>
              <option value="PROCESSING">PROCESSING</option>
              <option value="COMPLETED">COMPLETED</option>
              <option value="FAILED">FAILED</option>
            </select>
          </div>

          {(searchQuery || levelFilter !== "ALL" || statusFilter !== "ALL") && (
            <button
              onClick={() => {
                setSearchQuery("");
                setLevelFilter("ALL");
                setStatusFilter("ALL");
              }}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium px-2 py-1"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Logs Table */}
      {isLoading ? (
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
          <Skeleton height="h-8" width="w-48" />
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} height="h-12" />
          ))}
        </div>
      ) : error ? (
        <div className="p-8 bg-rose-500/5 border border-rose-500/20 rounded-xl text-center space-y-3">
          <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto" />
          <h3 className="text-sm font-bold text-rose-300">Failed to Load Container Logs</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Unable to fetch logs for container {decodedContainerName}. Please check backend connection.
          </p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded-lg hover:bg-rose-500/30 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      ) : filteredLogs.length === 0 ? (
        <div className="p-12 bg-slate-900/40 border border-slate-800 rounded-xl text-center space-y-3">
          <Terminal className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-sm font-semibold text-slate-300">No Container Logs Found</h3>
          <p className="text-xs text-slate-500">
            {logs && logs.length > 0
              ? "No log entries match your active search or filters for this container."
              : `No log events recorded for container ${decodedContainerName}.`}
          </p>
        </div>
      ) : (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/80 border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3.5">Timestamp</th>
                  <th className="px-4 py-3.5">Level</th>
                  <th className="px-4 py-3.5">Message</th>
                  <th className="px-4 py-3.5">Container</th>
                  <th className="px-4 py-3.5">Host / Server</th>
                  <th className="px-4 py-3.5">Status</th>
                  <th className="px-4 py-3.5 text-center">Count</th>
                  <th className="px-4 py-3.5">Correlation Group</th>
                  <th className="px-4 py-3.5 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredLogs.map((log) => {
                  const levelStyle = levelStyles[log.level] || levelStyles.INFO;
                  const statusStyle = statusStyles[log.status] || statusStyles.CLOSED;
                  const containerLabel = log.container_name || log.application_name || "app-service";
                  const hostLabel = log.host || log.server_name || "cluster-node";

                  return (
                    <tr
                      key={log.id}
                      onClick={() => setSelectedLog(log)}
                      className="hover:bg-slate-800/40 cursor-pointer transition-colors duration-150 group"
                    >
                      <td className="px-4 py-3 whitespace-nowrap text-slate-400 font-mono text-[11px]">
                        <div className="flex items-center gap-1.5">
                          <Clock className="w-3 h-3 text-slate-500" />
                          <span>
                            {new Date(log.timestamp).toLocaleString("en-US", {
                              hour12: false,
                              month: "short",
                              day: "2-digit",
                              hour: "2-digit",
                              minute: "2-digit",
                              second: "2-digit",
                            })}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold border ${levelStyle.bg} ${levelStyle.text} ${levelStyle.border}`}
                        >
                          {log.level}
                        </span>
                      </td>
                      <td className="px-4 py-3 max-w-xs font-mono text-[11px] text-slate-200 truncate">
                        {log.message}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="flex items-center gap-1.5 text-indigo-300 font-medium font-mono">
                          <Boxes className="w-3 h-3 text-indigo-400" />
                          <span>{containerLabel}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-slate-400">
                        <div className="flex items-center gap-1.5">
                          <Server className="w-3 h-3 text-slate-500" />
                          <span>{hostLabel}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold border ${statusStyle.bg} ${statusStyle.text} ${statusStyle.border}`}
                        >
                          {log.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-center">
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px] font-semibold">
                          {log.occurrence_count || 1}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        {log.correlation_group_id ? (
                          <span className="font-mono text-[10px] text-indigo-300 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                            {log.correlation_group_id.slice(0, 8)}...
                          </span>
                        ) : (
                          <span className="text-slate-600 text-[10px]">None</span>
                        )}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-right">
                        <button className="text-slate-400 group-hover:text-indigo-400 p-1 rounded-lg hover:bg-slate-800 transition-colors">
                          <Maximize2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Log Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-hidden flex flex-col shadow-2xl animate-fade-in">
            <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  <Terminal className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Log Event Details</h3>
                  <p className="text-xs text-slate-400 font-mono">Log ID: {selectedLog.id}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedLog(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-5">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-slate-950/60 rounded-xl border border-slate-800">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Level</span>
                  <div className="mt-1">
                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${levelStyles[selectedLog.level]?.text || "text-slate-300"}`}>
                      {selectedLog.level}
                    </span>
                  </div>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Status</span>
                  <div className="mt-1 text-xs font-semibold text-slate-200">{selectedLog.status}</div>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Occurrences</span>
                  <div className="mt-1 text-xs font-semibold text-slate-200">{selectedLog.occurrence_count || 1}</div>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Host</span>
                  <div className="mt-1 text-xs font-semibold text-slate-200">{selectedLog.host || selectedLog.server_name || "N/A"}</div>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 mb-2 block">Message</label>
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-rose-300 leading-relaxed overflow-x-auto whitespace-pre-wrap select-all">
                  {selectedLog.message}
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Metadata & Timestamps</h4>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                    <span className="text-slate-400">Timestamp</span>
                    <span className="font-mono text-slate-200">{new Date(selectedLog.timestamp).toISOString()}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                    <span className="text-slate-400">Container Name</span>
                    <span className="font-semibold text-indigo-400 font-mono">{selectedLog.container_name || selectedLog.application_name || "N/A"}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                    <span className="text-slate-400">Fingerprint</span>
                    <span className="font-mono text-slate-300">{selectedLog.fingerprint || "N/A"}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                    <span className="text-slate-400">Correlation Group ID</span>
                    <span className="font-mono text-slate-300">{selectedLog.correlation_group_id || "None"}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex justify-end">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-xl transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
