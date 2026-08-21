import React from "react";
import { Card } from "./Card";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: "increase" | "decrease" | "neutral";
  subtitle?: string;
  icon?: React.ReactNode;
  statusColor?: "emerald" | "amber" | "rose" | "indigo" | "cyan";
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  changeType = "neutral",
  subtitle,
  icon,
  statusColor = "indigo",
}) => {
  const accentColors = {
    emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    amber: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    rose: "text-rose-400 bg-rose-500/10 border-rose-500/20",
    indigo: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
    cyan: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
  };

  return (
    <Card className="hover:border-slate-700/80 transition-all duration-200">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</p>
          <h4 className="text-2xl font-bold text-slate-50 mt-1 tracking-tight">{value}</h4>
        </div>
        {icon && (
          <div className={`p-2.5 rounded-xl border ${accentColors[statusColor]}`}>
            {icon}
          </div>
        )}
      </div>

      <div className="mt-4 flex items-center justify-between pt-3 border-t border-slate-800/60 text-xs">
        {change && (
          <div className="flex items-center gap-1">
            {changeType === "increase" && <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />}
            {changeType === "decrease" && <TrendingDown className="w-3.5 h-3.5 text-rose-400" />}
            {changeType === "neutral" && <Minus className="w-3.5 h-3.5 text-slate-400" />}
            <span
              className={`font-semibold ${
                changeType === "increase"
                  ? "text-emerald-400"
                  : changeType === "decrease"
                  ? "text-rose-400"
                  : "text-slate-400"
              }`}
            >
              {change}
            </span>
          </div>
        )}
        {subtitle && <span className="text-slate-400 text-xs ml-auto">{subtitle}</span>}
      </div>
    </Card>
  );
};
