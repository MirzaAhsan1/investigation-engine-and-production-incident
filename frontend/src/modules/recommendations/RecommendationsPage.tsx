import { useState } from "react";
import { Sparkles, AlertTriangle, Clock, Zap, Info } from "lucide-react";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Modal } from "../../components/ui/Modal";
import { ActionStatusBadge } from "../../components/ui/ActionStatusBadge";
import { ApproveRejectButtons } from "../../components/ui/ApproveRejectButtons";
import { useGetRecommendationsQuery, useApproveRecommendationMutation, useRejectRecommendationMutation } from "../../api/recommendationsApi";

const staticRecommendations = [
  {
    id: "REC-089",
    incidentId: "INC-1041",
    title: "Kill idle Postgres connections & restart analytics-worker",
    actionType: "FLUSH_DB_CONNECTIONS",
    description: "Terminate all idle connections older than 10 minutes on postgres-primary using pg_terminate_backend. Then scale analytics-worker to 0 to stop the connection leak before redeploying the patched version.",
    confidenceScore: 97,
    riskLevel: "LOW",
    estimatedRecoveryMin: 3,
    automatedScript: "kubectl scale deployment analytics-worker --replicas=0 -n prod\npsql $DB_URL -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND query_start < NOW() - INTERVAL '10 minutes';\"",
    status: "PENDING",
    createdAt: "2026-07-23 19:32",
  },
  {
    id: "REC-088",
    incidentId: "INC-1039",
    title: "Flush Redis cache and restart replica nodes",
    actionType: "CLEAR_REDIS_CACHE",
    description: "The cache miss rate spike indicates stale or corrupted cache entries. A FLUSHDB followed by a rolling restart of replica nodes will restore hit rates.",
    confidenceScore: 88,
    riskLevel: "MEDIUM",
    estimatedRecoveryMin: 8,
    automatedScript: "redis-cli -h $REDIS_HOST FLUSHDB\nkubectl rollout restart deployment/redis-replica -n prod",
    status: "PENDING",
    createdAt: "2026-07-23 14:05",
  },
  {
    id: "REC-087",
    incidentId: "INC-1042",
    title: "Rollback api-gateway to stable version v2.3.1",
    actionType: "ROLLBACK_DEPLOYMENT",
    description: "The latency regression correlates with the v2.4.0 deployment. Rolling back to v2.3.1 will immediately restore baseline performance while the root cause is investigated.",
    confidenceScore: 94,
    riskLevel: "LOW",
    estimatedRecoveryMin: 2,
    automatedScript: "kubectl rollout undo deployment/api-gateway -n prod\nkubectl rollout status deployment/api-gateway -n prod",
    status: "APPROVED",
    createdAt: "2026-07-23 19:50",
  },
  {
    id: "REC-086",
    incidentId: "INC-1040",
    title: "Scale payment-svc replicas from 4 to 8",
    actionType: "SCALE_REPLICAS",
    description: "Traffic surge is saturating the existing 4 replicas. Scaling to 8 will distribute load and reduce per-pod error rate below the 0.1% SLO threshold.",
    confidenceScore: 91,
    riskLevel: "LOW",
    estimatedRecoveryMin: 90,
    automatedScript: "kubectl scale deployment payment-svc --replicas=8 -n prod",
    status: "EXECUTED",
    createdAt: "2026-07-23 17:52",
  },
];

const riskColors: Record<string, string> = {
  CRITICAL: "text-rose-400",
  HIGH: "text-orange-400",
  MEDIUM: "text-amber-400",
  LOW: "text-emerald-400",
};

export default function RecommendationsPage() {
  const { data: apiRecommendations } = useGetRecommendationsQuery();
  const [approveRec] = useApproveRecommendationMutation();
  const [rejectRec] = useRejectRecommendationMutation();

  const [selected, setSelected] = useState<any>(null);

  const recommendations = apiRecommendations && apiRecommendations.length > 0 ? apiRecommendations : staticRecommendations;

  const pending = recommendations.filter((r) => r.status === "PENDING");
  const completed = recommendations.filter((r) => r.status !== "PENDING");

  const handleApprove = async (id: string) => {
    try {
      await approveRec(id).unwrap();
    } catch {
      // Handled via RTK Query
    }
  };

  const handleReject = async (id: string) => {
    try {
      await rejectRec(id).unwrap();
    } catch {
      // Handled via RTK Query
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-50 tracking-tight">AI Recommendations & Action Queue</h1>
          <p className="text-sm text-slate-400 mt-0.5">AI-generated remediation playbooks — approve to trigger execution</p>
        </div>
        <div className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg bg-violet-500/10 border border-violet-500/20 text-violet-300 font-medium">
          <Sparkles className="w-3.5 h-3.5 animate-pulse" />
          {pending.length} actions pending approval
        </div>
      </div>

      {pending.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" /> Awaiting Approval
          </h2>
          <div className="grid gap-3">
            {pending.map((rec: any) => (
              <Card key={rec.id} variant="glow" className="hover:border-violet-500/40 transition-colors">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1.5">
                      <span className="text-[10px] font-mono text-violet-400 font-bold">{rec.id}</span>
                      {rec.incidentId && <span className="text-[10px] font-mono text-slate-500">{rec.incidentId}</span>}
                    </div>
                    <p className="text-sm font-semibold text-slate-100">{rec.title}</p>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2">{rec.description || rec.title}</p>
                  </div>
                  <div className="flex flex-col items-end gap-2 flex-shrink-0">
                    {rec.riskLevel && <span className={`text-xs font-bold ${riskColors[rec.riskLevel]}`}>Risk: {rec.riskLevel}</span>}
                    {rec.estimatedRecoveryMin && (
                      <div className="flex items-center gap-1.5">
                        <Clock className="w-3 h-3 text-slate-500" />
                        <span className="text-xs text-slate-400">{rec.estimatedRecoveryMin}m recovery</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-800/60 flex items-center justify-between gap-3 flex-wrap">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5 text-violet-400" />
                      <div className="h-1.5 w-20 bg-slate-800 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full" style={{ width: `${rec.confidenceScore || 95}%` }} />
                      </div>
                      <span className="text-xs font-bold text-violet-300">{rec.confidenceScore || 95}%</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {rec.automatedScript && (
                      <Button variant="ghost" size="sm" onClick={() => setSelected(rec)} leftIcon={<Info className="w-3.5 h-3.5" />}>
                        Details
                      </Button>
                    )}
                    <ApproveRejectButtons
                      status={rec.status}
                      onApprove={() => handleApprove(rec.id)}
                      onReject={() => handleReject(rec.id)}
                    />
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {completed.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-slate-300">History</h2>
          <div className="grid gap-2">
            {completed.map((rec: any) => (
              <div key={rec.id} className="flex items-center justify-between gap-4 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/60 opacity-70 hover:opacity-100 transition-opacity">
                <div>
                  <span className="text-xs font-mono text-slate-500">{rec.id}</span>
                  <p className="text-sm text-slate-300 mt-0.5">{rec.title}</p>
                </div>
                <ActionStatusBadge status={rec.status} />
              </div>
            ))}
          </div>
        </div>
      )}

      <Modal isOpen={!!selected} onClose={() => setSelected(null)} title={selected?.id || ""} maxWidth="xl">
        {selected && (
          <div className="space-y-4">
            <p className="text-sm text-slate-300">{selected.description}</p>
            {selected.automatedScript && (
              <div>
                <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Automated Script</p>
                <pre className="font-mono text-xs text-emerald-300 bg-slate-950 border border-slate-800 rounded-xl p-4 overflow-x-auto whitespace-pre-wrap">
                  {selected.automatedScript}
                </pre>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
