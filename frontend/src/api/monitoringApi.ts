import { baseApi } from "./baseApi";
import { QUERY_TAGS } from "../constants/queryTags";

export interface SystemMetrics {
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  networkInMbps: number;
  networkOutMbps: number;
  activeDbConnections: number;
  apiErrorRatePct: number;
  avgLatencyMs: number;
  services: Array<{
    name: string;
    status: "OPERATIONAL" | "DEGRADED" | "OUTAGE";
    uptimePct: number;
    latencyMs: number;
    errorRate: number;
  }>;
}

export interface ServerStat {
  server_id: string;
  name: string;
  host: string;
  environment: string;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  error_rate: number;
  open_incidents_count: number;
  timestamp: string | null;
}

export const monitoringApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getMonitoringMetrics: builder.query<SystemMetrics, void>({
      query: () => "/api/monitoring/metrics",
      providesTags: [QUERY_TAGS.MONITORING],
    }),
    getServerStats: builder.query<ServerStat[], void>({
      query: () => "/api/servers/stats",
      providesTags: [QUERY_TAGS.MONITORING],
    }),
  }),
});

export const { useGetMonitoringMetricsQuery, useGetServerStatsQuery } = monitoringApi;
