import { baseApi } from "./baseApi";
import { QUERY_TAGS } from "../constants/queryTags";
import { ACTION_ENDPOINTS } from "../constants/endpoints";
import type { InvestigationAction, ActionApproveRejectPayload } from "../types/actions";

export const actionsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getInvestigationActions: builder.query<InvestigationAction[], string>({
      query: (investigationId) => ACTION_ENDPOINTS.GET_BY_INVESTIGATION(investigationId),
      providesTags: (result, _error, investigationId) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: QUERY_TAGS.ACTION_QUEUE, id })),
              { type: QUERY_TAGS.ACTION_QUEUE, id: investigationId },
            ]
          : [{ type: QUERY_TAGS.ACTION_QUEUE, id: investigationId }],
    }),

    approveAction: builder.mutation<InvestigationAction, ActionApproveRejectPayload>({
      query: ({ action_id, approved_by }) => ({
        url: ACTION_ENDPOINTS.APPROVE(action_id),
        method: "POST",
        body: { approved_by },
      }),
      invalidatesTags: [QUERY_TAGS.ACTION_QUEUE, QUERY_TAGS.RECOMMENDATION],
    }),

    rejectAction: builder.mutation<InvestigationAction, ActionApproveRejectPayload>({
      query: ({ action_id, approved_by }) => ({
        url: ACTION_ENDPOINTS.REJECT(action_id),
        method: "POST",
        body: { approved_by },
      }),
      invalidatesTags: [QUERY_TAGS.ACTION_QUEUE, QUERY_TAGS.RECOMMENDATION],
    }),
  }),
});

export const {
  useGetInvestigationActionsQuery,
  useLazyGetInvestigationActionsQuery,
  useApproveActionMutation,
  useRejectActionMutation,
} = actionsApi;
