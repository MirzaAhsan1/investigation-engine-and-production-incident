import React, { useState } from "react";
import { Zap, AlertTriangle } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "./Card";
import { ActionStatusBadge } from "./ActionStatusBadge";
import { ApproveRejectButtons } from "./ApproveRejectButtons";
import { Skeleton } from "./Skeleton";
import type { InvestigationAction } from "../../types/actions";
import { useApproveActionMutation, useRejectActionMutation } from "../../api/actionsApi";
import useAuthStore from "../../store/authStore";

interface RecommendedActionsTableProps {
  actions?: InvestigationAction[];
  isLoading?: boolean;
  error?: string | null;
}

export const RecommendedActionsTable: React.FC<RecommendedActionsTableProps> = ({
  actions = [],
  isLoading = false,
  error = null,
}) => {
  const user = useAuthStore((state) => state.user);
  const currentUserId = user?.id || user?.sub || "00000000-0000-0000-0000-000000000000";

  const [approveAction] = useApproveActionMutation();
  const [rejectAction] = useRejectActionMutation();

  const [actionInProgress, setActionInProgress] = useState<Record<string, "approving" | "rejecting" | null>>({});
  const [apiError, setApiError] = useState<string | null>(null);

  const handleApprove = async (actionId: string) => {
    setApiError(null);
    setActionInProgress((prev) => ({ ...prev, [actionId]: "approving" }));
    try {
      await approveAction({ action_id: actionId, approved_by: currentUserId }).unwrap();
    } catch (err: any) {
      setApiError(err?.data?.detail || "Failed to approve action. Please try again.");
    } finally {
      setActionInProgress((prev) => ({ ...prev, [actionId]: null }));
    }
  };

  const handleReject = async (actionId: string) => {
    setApiError(null);
    setActionInProgress((prev) => ({ ...prev, [actionId]: "rejecting" }));
    try {
      await rejectAction({ action_id: actionId, approved_by: currentUserId }).unwrap();
    } catch (err: any) {
      setApiError(err?.data?.detail || "Failed to reject action. Please try again.");
    } finally {
      setActionInProgress((prev) => ({ ...prev, [actionId]: null }));
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle><Zap className="w-4 h-4 text-violet-400" /> Recommended Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} height="h-16" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card variant="glow">
      <CardHeader>
        <div className="flex items-center justify-between w-full">
          <CardTitle><Zap className="w-4 h-4 text-violet-400" /> Recommended Actions</CardTitle>
          <span className="text-xs text-slate-400">{actions.length} action{actions.length === 1 ? "" : "s"} generated</span>
        </div>
      </CardHeader>

      <CardContent>
        {(error || apiError) && (
          <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>{error || apiError}</span>
          </div>
        )}

        {actions.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs">
            No recommended actions available for this investigation yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            {/* Desktop Table View */}
            <table className="w-full text-left text-xs border-collapse hidden md:table">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                  <th className="pb-3 px-2">Priority</th>
                  <th className="pb-3 px-2">Title</th>
                  <th className="pb-3 px-2">Action Type</th>
                  <th className="pb-3 px-2">Provider</th>
                  <th className="pb-3 px-2">Target</th>
                  <th className="pb-3 px-2">Confidence</th>
                  <th className="pb-3 px-2">Status</th>
                  <th className="pb-3 px-2 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {actions.map((act) => {
                  const state = actionInProgress[act.id];
                  return (
                    <React.Fragment key={act.id}>
                      <tr className="hover:bg-slate-900/40 transition-colors">
                        <td className="py-3.5 px-2">
                          <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-800 text-violet-300 font-bold text-xs">
                            P{act.priority}
                          </span>
                        </td>
                        <td className="py-3.5 px-2 font-medium text-slate-100 max-w-[220px] truncate">
                          {act.title}
                        </td>
                        <td className="py-3.5 px-2 font-mono text-[11px] text-indigo-400">
                          {act.action_type}
                        </td>
                        <td className="py-3.5 px-2">
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px] uppercase">
                            {act.provider || "coolify"}
                          </span>
                        </td>
                        <td className="py-3.5 px-2 font-mono text-[11px] text-slate-300">
                          {act.target}
                        </td>
                        <td className="py-3.5 px-2 font-semibold text-violet-300">
                          {Math.round(act.confidence)}%
                        </td>
                        <td className="py-3.5 px-2">
                          <ActionStatusBadge status={act.status} />
                        </td>
                        <td className="py-3.5 px-2 text-right">
                          <div className="flex justify-end">
                            <ApproveRejectButtons
                              status={act.status}
                              onApprove={() => handleApprove(act.id)}
                              onReject={() => handleReject(act.id)}
                              isLoadingApprove={state === "approving"}
                              isLoadingReject={state === "rejecting"}
                            />
                          </div>
                        </td>
                      </tr>
                      {act.execution_log && (
                        <tr>
                          <td colSpan={8} className="px-4 py-2.5 bg-slate-950/40 border-b border-slate-800/40">
                            <div className="space-y-1">
                              <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Execution Log</p>
                              <pre className="font-mono text-[11px] text-emerald-400 bg-slate-950 p-2.5 rounded-lg border border-slate-900 overflow-x-auto whitespace-pre-wrap max-h-40">
                                {act.execution_log}
                              </pre>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>

            {/* Mobile Card View */}
            <div className="space-y-3 md:hidden">
              {actions.map((act) => {
                const state = actionInProgress[act.id];
                return (
                  <div key={act.id} className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-slate-800 text-violet-300 font-bold text-[10px] flex items-center justify-center">
                          P{act.priority}
                        </span>
                        <span className="font-mono text-[10px] text-indigo-400">{act.action_type}</span>
                      </div>
                      <ActionStatusBadge status={act.status} />
                    </div>

                    <div>
                      <p className="text-sm font-semibold text-slate-100">{act.title}</p>
                      <div className="flex flex-wrap items-center gap-3 mt-1 text-xs text-slate-400">
                        <span>Target: <code className="text-slate-300">{act.target}</code></span>
                        <span>·</span>
                        <span className="text-violet-300 font-bold">{Math.round(act.confidence)}% Confidence</span>
                        <span>·</span>
                        <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono text-[9px] uppercase">{act.provider || "coolify"}</span>
                      </div>
                    </div>

                    {act.execution_log && (
                      <div className="p-2.5 bg-slate-950 border border-slate-900 rounded-lg space-y-1">
                        <p className="text-[9px] font-semibold text-slate-500 uppercase tracking-wider">Execution Log</p>
                        <pre className="font-mono text-[10px] text-emerald-400 whitespace-pre-wrap max-h-32 overflow-y-auto">
                          {act.execution_log}
                        </pre>
                      </div>
                    )}

                    <div className="pt-2 border-t border-slate-800/60 flex justify-end">
                      <ApproveRejectButtons
                        status={act.status}
                        onApprove={() => handleApprove(act.id)}
                        onReject={() => handleReject(act.id)}
                        isLoadingApprove={state === "approving"}
                        isLoadingReject={state === "rejecting"}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
