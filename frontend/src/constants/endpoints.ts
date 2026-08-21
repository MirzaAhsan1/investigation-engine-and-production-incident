export const AUTH_ENDPOINTS = {
  LOGIN: "/api/auth/login",
  REGISTER: "/api/auth/register",
  ME: "/api/auth/me",
} as const;

export const INCIDENT_ENDPOINTS = {
  GET_ALL: "/api/incidents/",
  GET_BY_ID: (id: string) => `/api/incidents/${id}`,
  CREATE: "/api/incidents/",
} as const;

export const EVIDENCE_ENDPOINTS = {
  GET_BY_INCIDENT: (incidentId: string) => `/api/evidence/${incidentId}`,
  CREATE: "/api/evidence/",
} as const;

export const INVESTIGATION_ENDPOINTS = {
  START: "/api/investigations/",
  GET_BY_INCIDENT: (incidentId: string) => `/api/investigations/${incidentId}`,
  GET_REPORT: (incidentId: string) => `/api/investigations/report/${incidentId}`,
} as const;

export const ACTION_ENDPOINTS = {
  GET_BY_INVESTIGATION: (investigationId: string) => `/api/actions/investigation/${investigationId}`,
  APPROVE: (actionId: string) => `/api/actions/${actionId}/approve`,
  REJECT: (actionId: string) => `/api/actions/${actionId}/reject`,
} as const;


