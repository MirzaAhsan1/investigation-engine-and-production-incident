export interface InvestigationAction {
  id: string;
  investigation_id: string;
  title: string;
  action_type: string;
  target: string;
  priority: number;
  confidence: number;
  status: "PENDING" | "PENDING_APPROVAL" | "APPROVED" | "REJECTED" | "PENDING_EXECUTION" | "EXECUTED" | "FAILED" | string;
  provider: string;
  approved_by?: string | null;
  execution_log?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface ApproveActionRequest {
  approved_by: string;
}

export interface RejectActionRequest {
  approved_by: string;
}

export interface ActionApproveRejectPayload {
  action_id: string;
  approved_by: string;
}
