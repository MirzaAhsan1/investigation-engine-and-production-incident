import { baseApi } from "./baseApi";
import { QUERY_TAGS } from "../constants/queryTags";

export interface Recommendation {
  id: string;
  incidentId: string;
  incidentTitle: string;
  title: string;
  actionType: "REBOOT_PODS" | "SCALE_REPLICAS" | "ROLLBACK_DEPLOYMENT" | "CLEAR_REDIS_CACHE" | "FLUSH_DB_CONNECTIONS";
  confidenceScore: number;
  riskLevel: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  estimatedRecoveryMin: number;
  description: string;
  automatedScript: string;
  status: "PENDING" | "APPROVED" | "REJECTED" | "EXECUTING" | "EXECUTED";
  createdAt: string;
}

export const recommendationsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getRecommendations: builder.query<Recommendation[], void>({
      query: () => "/api/recommendations",
      providesTags: [QUERY_TAGS.RECOMMENDATION],
    }),
    approveRecommendation: builder.mutation<{ success: boolean; message: string }, string>({
      query: (id) => ({
        url: `/api/recommendations/${id}/approve`,
        method: "POST",
      }),
      invalidatesTags: [QUERY_TAGS.RECOMMENDATION, QUERY_TAGS.INCIDENT],
    }),
    rejectRecommendation: builder.mutation<{ success: boolean; message: string }, string>({
      query: (id) => ({
        url: `/api/recommendations/${id}/reject`,
        method: "POST",
      }),
      invalidatesTags: [QUERY_TAGS.RECOMMENDATION],
    }),
  }),
});

export const {
  useGetRecommendationsQuery,
  useApproveRecommendationMutation,
  useRejectRecommendationMutation,
} = recommendationsApi;
