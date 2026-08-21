import React from "react";
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from "lucide-react";
import { useToast } from "../../hooks/useToast";

const icons = {
  success: <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />,
  error: <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />,
  warning: <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />,
  info: <Info className="w-4 h-4 text-indigo-400 flex-shrink-0" />,
};

const borderColors = {
  success: "border-emerald-500/30 bg-emerald-500/10",
  error: "border-rose-500/30 bg-rose-500/10",
  warning: "border-amber-500/30 bg-amber-500/10",
  info: "border-indigo-500/30 bg-indigo-500/10",
};

export const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto p-4 rounded-xl border backdrop-blur-md shadow-2xl flex items-start justify-between gap-3 text-xs transition-all duration-300 animate-in slide-in-from-bottom-5 ${
            borderColors[toast.type]
          }`}
        >
          <div className="flex items-start gap-2.5">
            {icons[toast.type]}
            <div>
              <p className="font-semibold text-slate-100">{toast.title}</p>
              <p className="text-slate-300 mt-0.5">{toast.message}</p>
            </div>
          </div>
          <button
            onClick={() => removeToast(toast.id)}
            className="p-1 text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-800/60 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
};
