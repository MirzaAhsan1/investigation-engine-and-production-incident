import { baseApi } from "./baseApi";
import { QUERY_TAGS } from "../constants/queryTags";
import { AUTH_ENDPOINTS } from "../constants/endpoints";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface UserProfileResponse {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export const authApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation<LoginResponse, LoginRequest>({
      query: (credentials) => ({
        url: AUTH_ENDPOINTS.LOGIN,
        method: "POST",
        body: credentials,
      }),
      invalidatesTags: [QUERY_TAGS.AUTH, QUERY_TAGS.USER],
    }),

    register: builder.mutation<UserProfileResponse, RegisterRequest>({
      query: (userData) => ({
        url: AUTH_ENDPOINTS.REGISTER,
        method: "POST",
        body: userData,
      }),
      invalidatesTags: [QUERY_TAGS.AUTH],
    }),

    getMe: builder.query<UserProfileResponse, void>({
      query: () => AUTH_ENDPOINTS.ME,
      providesTags: [QUERY_TAGS.USER],
    }),
  }),
});

export const { useLoginMutation, useRegisterMutation, useGetMeQuery, useLazyGetMeQuery } = authApi;