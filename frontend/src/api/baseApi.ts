import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from "@reduxjs/toolkit/query";

import { QUERY_TAGS } from "../constants/queryTags";
import useAuthStore from "../store/authStore";

// Configure base query with token injection
const baseQuery = fetchBaseQuery({
  baseUrl: import.meta.env.VITE_API_BASE_URL,
  prepareHeaders: (headers) => {
    // Pull the token dynamically from the global store (or fallback to localStorage)
    const token = useAuthStore.getState().accessToken || localStorage.getItem("accessToken");
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
    return headers;
  },
});

// Global Request Guard: Intercept 401 Unauthorized errors
const baseQueryWithReauth: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  let result = await baseQuery(args, api, extraOptions);

  if (result.error && result.error.status === 401) {
    // If an API request fails due to an expired token, clear the session
    useAuthStore.getState().logout();
    
    // Force-redirect the user to /login
    window.location.href = "/login";
  }
  
  return result;
};

export const baseApi = createApi({
  reducerPath: "baseApi",
  baseQuery: baseQueryWithReauth,
  tagTypes: Object.values(QUERY_TAGS),
  endpoints: () => ({}),
});