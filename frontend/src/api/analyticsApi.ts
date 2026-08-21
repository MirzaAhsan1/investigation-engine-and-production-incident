import { baseApi } from "./baseApi";
import { QUERY_TAGS } from "../constants/queryTags";

export interface AnalyticsSummary {
  mttrMinutes: number;
  mtbfHours: number;
  aiPrecisionPct: number;
  systemAvailabilityPct: number;
  totalIncidentsMonth: number;
  severityDistribution: Array<{ name: string; value: number }>;
  incidentTrend: Array<{ date: string; count: number; resolved: number }>;
  topRootCauses: Array<{ cause: string; frequency: number; avgResolutionMin: number }>;
}

export const analyticsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getAnalyticsSummary: builder.query<AnalyticsSummary, void>({
      query: () => "/api/analytics/summary",
      providesTags: [QUERY_TAGS.ANALYTICS],
    }),
  }),
});

export const { useGetAnalyticsSummaryQuery } = analyticsApi;
