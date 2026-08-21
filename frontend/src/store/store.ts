import { configureStore } from "@reduxjs/toolkit";
import { baseApi } from "../api/baseApi";

// Import all injected APIs so their endpoints are registered
import "../api/authApi";
import "../api/incidentsApi";
import "../api/evidenceApi";
import "../api/investigationApi";
import "../api/monitoringApi";
import "../api/recommendationsApi";
import "../api/analyticsApi";
import "../api/actionsApi";


export const store = configureStore({
  reducer: {
    [baseApi.reducerPath]: baseApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(baseApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;