import { baseApi } from "./baseApi";
import { QUERY_TAGS } from "../constants/queryTags";
import { INCIDENT_ENDPOINTS } from "../constants/endpoints";

export interface BackendIncident {
  id: string;
  title: string;
  description: string;
  incident_type: "SECURITY" | "APPLICATION" | "DATABASE" | "NETWORK" | "CLOUD" | "ENDPOINT" | "EMAIL" | "OTHER" | string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | string;
  status: "OPEN" | "IN_PROGRESS" | "RESOLVED" | "CLOSED" | string;
  source: "MANUAL" | "API" | "EMAIL" | "SIEM" | "MONITORING" | "AI" | string;
  reported_by: string;
  assigned_to?: string | null;
  application_id?: string | null;
  application?: {
    id: string;
    server_id: string;
    name: string;
    container_name: string;
    provider?: string | null;
    resource_uuid?: string | null;
  } | null;
  investigation?: {
    id: string;
    predicted_category?: string | null;
    predicted_cause?: string | null;
    root_cause?: string | null;
    confidence?: number | null;
    risk_score?: number | null;
    analysis_status?: string | null;
  } | null;
  created_at: string;
  updated_at: string;
}

export interface CreateIncidentPayload {
  title: string;
  description: string;
  incident_type: string;
  severity: string;
  source: string;
}

export interface Incident {
  id: string;
  title: string;
  severity: string;
  status: string;
  service: string;
  environment: string;
  assignee: string;
  createdAt: string;
  updatedAt: string;
  aiConfidence: number;
  rootCauseSummary?: string;
  impactScore?: number;
  evidenceCount?: number;
  description?: string;
}

export const incidentsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getIncidents: builder.query<BackendIncident[], void>({
      query: () => INCIDENT_ENDPOINTS.GET_ALL,
      providesTags: [QUERY_TAGS.INCIDENT],
    }),
    getIncidentById: builder.query<BackendIncident, string>({
      query: (id) => INCIDENT_ENDPOINTS.GET_BY_ID(id),
      providesTags: (_result, _error, id) => [{ type: QUERY_TAGS.INCIDENT, id }],
    }),
    createIncident: builder.mutation<BackendIncident, CreateIncidentPayload>({
      query: (payload) => ({
        url: INCIDENT_ENDPOINTS.CREATE,
        method: "POST",
        body: payload,
      }),
      invalidatesTags: [QUERY_TAGS.INCIDENT],
    }),
  }),
});

export const {
  useGetIncidentsQuery,
  useGetIncidentByIdQuery,
  useCreateIncidentMutation,
} = incidentsApi;
