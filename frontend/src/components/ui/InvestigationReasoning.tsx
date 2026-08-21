import React from "react";
import { Brain } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "./Card";
import type { InvestigationResponse } from "../../api/investigationApi";

interface InvestigationReasoningProps {
  investigation?: InvestigationResponse | null;
}

export const InvestigationReasoning: React.FC<InvestigationReasoningProps> = ({
  investigation,
}) => {
  if (!investigation) return null;

  return (
    <Card variant="glow">
      <CardHeader>
        <CardTitle><Brain className="w-4 h-4 text-violet-400" /> Root Cause Analysis & Reasoning</CardTitle>
      </CardHeader>

      <CardContent>
        <div className="space-y-4 text-xs">
          <div>
            <p className="text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">Root Cause Hypothesis</p>
            <div className="p-4 bg-slate-950/90 rounded-xl border border-violet-500/20 text-sm text-slate-200 leading-relaxed font-sans">
              {investigation.root_cause || "Root cause analysis completed by AI SRE agent."}
            </div>
          </div>

          {investigation.reasoning && (
            <div>
              <p className="text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">Diagnostic Reasoning & Telemetry Evidence</p>
              <div className="p-4 bg-slate-950/80 rounded-xl border border-slate-800 text-xs text-slate-300 leading-relaxed font-sans whitespace-pre-wrap">
                {investigation.reasoning}
              </div>
            </div>
          )}

          {investigation.triggered_rules && investigation.triggered_rules.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">Triggered Diagnostic Rules</p>
              <div className="flex flex-wrap gap-2">
                {investigation.triggered_rules.map((rule, idx) => (
                  <span key={idx} className="px-2.5 py-1 rounded-lg bg-violet-500/10 border border-violet-500/20 text-violet-300 font-mono text-[11px]">
                    {rule}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
