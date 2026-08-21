import { baseApi } from "./baseApi";
import { QUERY_TAGS } from "../constants/queryTags";
import { INVESTIGATION_ENDPOINTS } from "../constants/endpoints";

export interface StartInvestigationPayload {
  incident_id: string;
}

export interface InvestigationResponse {
  id: string;
  incident_id: string;
  risk_score: number;
  confidence: number;
  predicted_category: string;
  predicted_cause: string;
  model_version: string | null;
  root_cause: string | null;
  reasoning: string | null;
  recommended_actions: string;
  triggered_rules: string[] | null;
  llm_confidence: number | null;
  analysis_status: string;
  created_at: string;
  updated_at: string;
}

export const investigationApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    startInvestigation: builder.mutation<InvestigationResponse, StartInvestigationPayload>({
      query: (payload) => ({
        url: INVESTIGATION_ENDPOINTS.START,
        method: "POST",
        body: payload,
      }),
      invalidatesTags: [QUERY_TAGS.INCIDENT, QUERY_TAGS.KNOWLEDGE_BASE],
    }),
    getInvestigationByIncident: builder.query<InvestigationResponse, string>({
      query: (incidentId) => INVESTIGATION_ENDPOINTS.GET_BY_INCIDENT(incidentId),
      providesTags: (_result, _error, id) => [{ type: QUERY_TAGS.INCIDENT, id }],
    }),
    getInvestigationReport: builder.query<any, string>({
      query: (incidentId) => INVESTIGATION_ENDPOINTS.GET_REPORT(incidentId),
      providesTags: (_result, _error, id) => [{ type: QUERY_TAGS.REPORT, id }],
    }),
  }),
});

export const {
  useStartInvestigationMutation,
  useGetInvestigationByIncidentQuery,
  useLazyGetInvestigationByIncidentQuery,
  useGetInvestigationReportQuery,
} = investigationApi;
