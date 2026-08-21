import { Outlet, Link } from "react-router-dom";
import { Cpu, ShieldCheck, Activity } from "lucide-react";

export default function AuthLayout() {
  return (
    <div className="min-h-screen w-full bg-[#0b0f17] flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md z-10">
        <div className="flex flex-col items-center mb-8 text-center">
          <Link to="/" className="flex items-center gap-2.5 mb-3 group">
            <div className="p-2.5 bg-gradient-to-tr from-violet-600 to-indigo-600 rounded-xl shadow-lg shadow-indigo-500/25 border border-indigo-400/30">
              <Cpu className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
              APIRS
            </span>
          </Link>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800 text-[11px] font-medium text-slate-400">
            <Activity className="w-3 h-3 text-emerald-400 animate-pulse" />
            <span>AI Production Incident Response System</span>
          </div>
        </div>

        <div className="glass-panel p-8 rounded-2xl border border-slate-800/80 shadow-2xl shadow-black/80">
          <Outlet />
        </div>

        <div className="mt-8 text-center text-xs text-slate-500 flex items-center justify-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-500/80" />
          <span>Enterprise Grade Security & ML Anomaly Detection</span>
        </div>
      </div>
    </div>
  );
}
