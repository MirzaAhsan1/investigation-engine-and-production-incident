import { baseApi } from "./baseApi";
import { QUERY_TAGS } from "../constants/queryTags";
import { EVIDENCE_ENDPOINTS } from "../constants/endpoints";

export interface CreateEvidencePayload {
  incident_id: string;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  api_latency: number;
  error_rate: number;
  db_connections: number;
  active_containers: number;
  http_5xx_count: number;
  http_4xx_count: number;
  request_per_second: number;
  restart_count: number;
  pod_restart_count: number;
  failed_login_attempts: number;
  database_timeout_count: number;
  packet_loss: number;
  disk_io_wait: number;
  network_latency: number;
  ssl_certificate_days_left: number;
  deployment_changed: boolean;
  service_name: string;
  environment: string;
  logs: string;
}

export interface EvidenceResponse {
  id: string;
  incident_id: string;
  log_count?: number;
  error_count?: number;
  warning_count?: number;
  first_seen?: string;
  last_seen?: string;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  api_latency: number;
  error_rate: number;
  db_connections: number;
  active_containers: number;
  http_5xx_count: number;
  http_4xx_count: number;
  request_per_second: number;
  restart_count: number;
  pod_restart_count: number;
  failed_login_attempts: number;
  database_timeout_count: number;
  packet_loss: number;
  disk_io_wait: number;
  network_latency: number;
  ssl_certificate_days_left: number;
  deployment_changed: boolean;
  service_name: string;
  environment: string;
  logs: any;
  created_at: string;
  updated_at: string;
}

export const evidenceApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    createEvidence: builder.mutation<EvidenceResponse, CreateEvidencePayload>({
      query: (payload) => ({
        url: EVIDENCE_ENDPOINTS.CREATE,
        method: "POST",
        body: payload,
      }),
      invalidatesTags: [QUERY_TAGS.INCIDENT, QUERY_TAGS.MONITORING],
    }),
    getEvidenceByIncident: builder.query<EvidenceResponse, string>({
      query: (incidentId) => EVIDENCE_ENDPOINTS.GET_BY_INCIDENT(incidentId),
      providesTags: (_result, _error, id) => [{ type: QUERY_TAGS.INCIDENT, id }],
    }),
  }),
});

export const {
  useCreateEvidenceMutation,
  useGetEvidenceByIncidentQuery,
  useLazyGetEvidenceByIncidentQuery,
} = evidenceApi;
