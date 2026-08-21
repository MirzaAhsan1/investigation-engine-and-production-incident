import { baseApi } from "./baseApi";
import { QUERY_TAGS } from "../constants/queryTags";

export interface LogItem {
  id: string;
  timestamp: string;
  level: "ERROR" | "WARN" | "INFO" | "DEBUG" | string;
  message: string;
  status: string;
  occurrence_count: number;
  first_seen: string;
  last_seen: string;
  fingerprint: string;
  correlation_group_id?: string | null;
  container_name?: string | null;
  host?: string | null;
  application_name?: string | null;
  server_name?: string | null;
  created_at: string;
  updated_at: string;
}

export interface GetLogsParams {
  search?: string;
  level?: string;
  status?: string;
  container_name?: string;
  correlation_group_id?: string;
  limit?: number;
}

export const logsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getLogs: builder.query<LogItem[], GetLogsParams | void>({
      query: (params) => {
        if (!params) return "/api/logs";
        const searchParams = new URLSearchParams();
        if (params.search) searchParams.set("search", params.search);
        if (params.level) searchParams.set("level", params.level);
        if (params.status) searchParams.set("status", params.status);
        if (params.container_name) searchParams.set("container_name", params.container_name);
        if (params.correlation_group_id) searchParams.set("correlation_group_id", params.correlation_group_id);
        if (params.limit) searchParams.set("limit", params.limit.toString());
        const queryString = searchParams.toString();
        return queryString ? `/api/logs?${queryString}` : "/api/logs";
      },
      providesTags: [QUERY_TAGS.INCIDENT, QUERY_TAGS.MONITORING],
    }),
  }),
});

export const { useGetLogsQuery } = logsApi;
