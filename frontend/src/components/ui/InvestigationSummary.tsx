import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "./Card";
import { Badge } from "./Badge";
import type { InvestigationResponse } from "../../api/investigationApi";

interface InvestigationSummaryProps {
  investigation?: InvestigationResponse | null;
}

export const InvestigationSummary: React.FC<InvestigationSummaryProps> = ({
  investigation,
}) => {
  if (!investigation) return null;

  const confidence = Math.round(investigation.confidence || investigation.llm_confidence || 95);

  return (
    <Card variant="glow">
      <CardHeader>
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-mono text-violet-400 font-bold">INVESTIGATION-ANALYSIS</span>
            <Badge variant="severity" severity={investigation.predicted_category as any}>
              {investigation.predicted_category}
            </Badge>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
              Status: {investigation.analysis_status}
            </span>
          </div>
          <CardTitle>AI Diagnostic Summary: {investigation.predicted_category}</CardTitle>
        </div>
        <div className="text-right">
          <p className="text-xs text-slate-500 mb-1">AI Confidence</p>
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-20 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full"
                style={{ width: `${confidence}%` }}
              />
            </div>
            <span className="text-sm font-bold text-violet-300">{confidence}%</span>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
          <div className="p-3 bg-slate-950/80 border border-slate-800/80 rounded-xl">
            <p className="text-slate-400 font-semibold mb-1">Predicted Category</p>
            <p className="text-sm font-bold text-indigo-400">{investigation.predicted_category}</p>
          </div>
          <div className="p-3 bg-slate-950/80 border border-slate-800/80 rounded-xl">
            <p className="text-slate-400 font-semibold mb-1">Predicted Cause</p>
            <p className="text-sm font-bold text-amber-400 break-words">{investigation.predicted_cause}</p>
          </div>
          <div className="p-3 bg-slate-950/80 border border-slate-800/80 rounded-xl">
            <p className="text-slate-400 font-semibold mb-1">Risk Score</p>
            <p className="text-sm font-bold text-rose-400">{investigation.risk_score} / 100</p>
          </div>
          <div className="p-3 bg-slate-950/80 border border-slate-800/80 rounded-xl">
            <p className="text-slate-400 font-semibold mb-1">LLM Confidence</p>
            <p className="text-sm font-bold text-violet-300">{confidence}%</p>
          </div>
          <div className="p-3 bg-slate-950/80 border border-slate-800/80 rounded-xl">
            <p className="text-slate-400 font-semibold mb-1">Model Version</p>
            <p className="text-sm font-bold text-slate-300">{investigation.model_version || "N/A"}</p>
          </div>
          <div className="p-3 bg-slate-950/80 border border-slate-800/80 rounded-xl">
            <p className="text-slate-400 font-semibold mb-1">Analysis Status</p>
            <p className="text-sm font-bold text-emerald-400">{investigation.analysis_status}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
