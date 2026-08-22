import { baseApi } from "./baseApi";
import { QUERY_TAGS } from "../constants/queryTags";

export interface ApplicationItem {
  id: string;
  server_id: string;
  name: string;
  container_name: string;
  provider: string;
  resource_uuid: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const applicationsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getApplications: builder.query<ApplicationItem[], void>({
      query: () => "/api/applications",
      providesTags: [QUERY_TAGS.MONITORING],
    }),
  }),
});

export const { useGetApplicationsQuery } = applicationsApi;
