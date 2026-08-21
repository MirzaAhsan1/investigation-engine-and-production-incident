import React from "react";

export type SeverityType = "P0" | "P1" | "P2" | "P3" | "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
export type StatusType = "OPEN" | "INVESTIGATING" | "MITIGATED" | "RESOLVED" | "OPERATIONAL" | "DEGRADED" | "OUTAGE" | "AI_ANALYZING";

export interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "severity" | "status" | "ai" | "outline";
  severity?: SeverityType;
  status?: StatusType;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "default",
  severity,
  status,
  className = "",
}) => {
  let colorStyles = "bg-slate-800 text-slate-300 border-slate-700";

  if (variant === "severity" && severity) {
    switch (severity.toUpperCase()) {
      case "P0":
      case "CRITICAL":
        colorStyles = "bg-rose-500/15 text-rose-400 border-rose-500/30 animate-pulse";
        break;
      case "P1":
      case "HIGH":
        colorStyles = "bg-orange-500/15 text-orange-400 border-orange-500/30";
        break;
      case "P2":
      case "MEDIUM":
        colorStyles = "bg-amber-500/15 text-amber-400 border-amber-500/30";
        break;
      case "P3":
      case "LOW":
        colorStyles = "bg-cyan-500/15 text-cyan-400 border-cyan-500/30";
        break;
    }
  } else if (variant === "status" && status) {
    switch (status.toUpperCase()) {
      case "OPEN":
      case "OUTAGE":
        colorStyles = "bg-rose-500/15 text-rose-400 border-rose-500/30";
        break;
      case "INVESTIGATING":
      case "DEGRADED":
        colorStyles = "bg-amber-500/15 text-amber-400 border-amber-500/30";
        break;
      case "MITIGATED":
        colorStyles = "bg-blue-500/15 text-blue-400 border-blue-500/30";
        break;
      case "RESOLVED":
      case "OPERATIONAL":
        colorStyles = "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
        break;
      case "AI_ANALYZING":
        colorStyles = "bg-violet-500/20 text-violet-300 border-violet-500/40 animate-pulse";
        break;
    }
  } else if (variant === "ai") {
    colorStyles = "bg-gradient-to-r from-violet-500/20 to-indigo-500/20 text-violet-300 border-violet-500/40";
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border backdrop-blur-sm tracking-wide ${colorStyles} ${className}`}
    >
      {children}
    </span>
  );
};
