import { useState } from "react";
import { Sparkles, Search, Clock, Brain, GitBranch, ShieldCheck } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { useGetIncidentsQuery } from "../../api/incidentsApi";
import { useStartInvestigationMutation, type InvestigationResponse } from "../../api/investigationApi";
import { useGetInvestigationActionsQuery } from "../../api/actionsApi";
import { RecommendedActionsTable } from "../../components/ui/RecommendedActionsTable";
import { InvestigationSummary } from "../../components/ui/InvestigationSummary";
import { InvestigationReasoning } from "../../components/ui/InvestigationReasoning";

const staticInvestigations = [
  {
    incidentId: "INC-1041",
    title: "Database Connection Pool Exhausted",
    hypothesis: "Connection leak introduced in analytics-worker v1.4.3 — missing db.close() in batch reporting loop.",
    confidence: 97,
    riskLevel: "CRITICAL",
    evidenceCount: 12,
    similarIncidents: [
      { id: "INC-0987", similarity: 91, resolution: "Scaled down analytics-worker, deployed hotfix" },
      { id: "INC-0854", similarity: 76, resolution: "Added connection pool cleanup cron job" },
    ],
    diagnosticSteps: [
      "Detected anomalous connection count spike",
      "Correlated with analytics-worker v1.4.3 deployment at 19:15",
      "Identified missing finally block in batch_report_worker.py:L148",
      "Validated against 2 similar historical incidents",
    ],
  },
];

export default function AIInvestigationPage() {
  const [query, setQuery] = useState("");
  const { data: incidents } = useGetIncidentsQuery();
  const [startInvestigation, { isLoading }] = useStartInvestigationMutation();
  const [activeInvestigation, setActiveInvestigation] = useState<InvestigationResponse | null>(null);

  const activeInvestigationId = activeInvestigation?.id || "";
  const {
    data: investigationActions,
    isLoading: isLoadingActions,
    error: actionsError,
  } = useGetInvestigationActionsQuery(activeInvestigationId, { skip: !activeInvestigationId });

  const handleAnalyzeClick = async () => {
    if (!incidents || incidents.length === 0) return;
    const targetIncident = incidents[0];
    try {
      const res = await startInvestigation({ incident_id: targetIncident.id }).unwrap();
      setActiveInvestigation(res);
    } catch {
      // Handled via RTK
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-50 tracking-tight">AI Investigation</h1>
          <p className="text-sm text-slate-400 mt-0.5">RAG-powered root cause analysis, log anomaly detection, and diagnostic reasoning</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-violet-500/10 border border-violet-500/20 text-xs text-violet-300">
          <Brain className="w-3.5 h-3.5 animate-pulse" /> AI Agent Active
        </div>
      </div>

      <Card variant="glow">
        <CardHeader>
          <CardTitle><Search className="w-4 h-4 text-violet-400" />Knowledge & Incident Investigation Query</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask AI: 'Why is the database connection pool exhausted?' or select active incident to analyze..."
              className="flex-1 px-4 py-2.5 text-sm bg-slate-950 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-600 focus:outline-none focus:border-violet-500"
            />
            <Button
              variant="ai"
              size="md"
              isLoading={isLoading}
              onClick={handleAnalyzeClick}
              leftIcon={<Sparkles className="w-4 h-4" />}
            >
              Analyze
            </Button>
          </div>

          <div className="mt-3 flex flex-wrap gap-2">
            {["Why is API latency high?", "What caused the last P0?", "Show similar DB incidents", "Latest anomalies"].map((q) => (
              <button
                key={q}
                onClick={() => setQuery(q)}
                className="text-xs px-3 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Dynamic API Investigation Result */}
      {activeInvestigation && (
        <div className="space-y-6">
          <InvestigationSummary investigation={activeInvestigation} />
          <InvestigationReasoning investigation={activeInvestigation} />
          <RecommendedActionsTable
            actions={investigationActions || []}
            isLoading={isLoadingActions}
            error={actionsError ? "Failed to fetch investigation actions" : null}
          />
        </div>
      )}

      {/* Static Fallback Demo Items */}
      {staticInvestigations.map((inv) => (
        <Card key={inv.incidentId} variant="glow">
          <CardHeader>
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-mono text-violet-400 font-bold">{inv.incidentId}</span>
                <Badge variant="severity" severity={inv.riskLevel as any}>{inv.riskLevel}</Badge>
              </div>
              <CardTitle>{inv.title}</CardTitle>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-500 mb-1">AI Confidence</p>
              <div className="flex items-center gap-1.5">
                <div className="h-2 w-24 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full"
                    style={{ width: `${inv.confidence}%` }}
                  />
                </div>
                <span className="text-sm font-bold text-violet-300">{inv.confidence}%</span>
              </div>
            </div>
          </CardHeader>

          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <div>
                <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider flex items-center gap-1.5">
                  <Brain className="w-3.5 h-3.5 text-violet-400" /> AI Hypothesis
                </p>
                <div className="p-3.5 bg-slate-950/80 rounded-xl border border-violet-500/10">
                  <p className="text-sm text-slate-200 leading-relaxed">{inv.hypothesis}</p>
                </div>

                <p className="text-xs font-semibold text-slate-400 mt-4 mb-2 uppercase tracking-wider flex items-center gap-1.5">
                  <GitBranch className="w-3.5 h-3.5 text-indigo-400" /> Diagnostic Steps
                </p>
                <div className="space-y-1.5">
                  {inv.diagnosticSteps.map((step, i) => (
                    <div key={i} className="flex items-start gap-2.5">
                      <span className="w-5 h-5 rounded-full bg-indigo-500/20 text-indigo-400 text-[10px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">{i + 1}</span>
                      <p className="text-xs text-slate-300">{step}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-indigo-400" /> Similar Past Incidents
                </p>
                <div className="space-y-2.5">
                  {inv.similarIncidents.map((sim) => (
                    <div key={sim.id} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60">
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-xs font-mono text-indigo-400 font-bold">{sim.id}</span>
                        <div className="flex items-center gap-1">
                          <div className="h-1 w-12 bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-violet-500 rounded-full" style={{ width: `${sim.similarity}%` }} />
                          </div>
                          <span className="text-[10px] font-semibold text-violet-300">{sim.similarity}%</span>
                        </div>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <ShieldCheck className="w-3 h-3 text-emerald-400 flex-shrink-0 mt-0.5" />
                        <p className="text-xs text-slate-400">{sim.resolution}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
