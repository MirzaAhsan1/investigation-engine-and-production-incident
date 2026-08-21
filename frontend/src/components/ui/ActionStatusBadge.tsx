import React from "react";

export type ActionStatus =
  | "PENDING"
  | "PENDING_EXECUTION"
  | "RUNNING"
  | "SUCCESS"
  | "FAILED"
  | "REJECTED"
  | string;

const statusStyles: Record<string, string> = {
  PENDING: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  APPROVED: "bg-teal-500/15 text-teal-400 border-teal-500/30",
  PENDING_EXECUTION: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  RUNNING: "bg-indigo-500/15 text-indigo-400 border-indigo-500/30",
  EXECUTED: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  COMPLETED: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  SUCCESS: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  FAILED: "bg-rose-500/15 text-rose-400 border-rose-500/30",
  REJECTED: "bg-slate-800 text-slate-400 border-slate-700",
};

interface ActionStatusBadgeProps {
  status: ActionStatus;
  className?: string;
}

export const ActionStatusBadge: React.FC<ActionStatusBadgeProps> = ({ status, className = "" }) => {
  const style = statusStyles[status] || statusStyles.REJECTED;

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${style} ${className}`}>
      {status}
    </span>
  );
};
