import { useEffect } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Activity,
  AlertTriangle,
  Sparkles,
  CheckCircle2,
  BookOpen,
  BarChart3,
  FileText,
  Settings,
  User,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Search,
  Bell,
  Cpu,
  ShieldCheck,
  Terminal,
  Boxes,
} from "lucide-react";
import { useUIStore } from "../store/uiStore";
import useAuthStore from "../store/authStore";
import { ToastContainer } from "../components/ui/ToastContainer";
import { useGetMeQuery } from "../api/authApi";

const navigationItems = [
  { path: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { path: "/monitoring", label: "Monitoring", icon: Activity },
  { path: "/incidents", label: "Incidents", icon: AlertTriangle, badge: "3" },
  { path: "/containers", label: "Containers", icon: Boxes },
  { path: "/logs", label: "Logs", icon: Terminal },
  { path: "/ai-investigation", label: "AI Investigation", icon: Sparkles },
  { path: "/recommendations", label: "Recommendations", icon: CheckCircle2, badge: "2" },
  { path: "/knowledge-base", label: "Knowledge Base", icon: BookOpen },
  { path: "/analytics", label: "Analytics", icon: BarChart3 },
  { path: "/reports", label: "Reports", icon: FileText },
  { path: "/settings", label: "Settings", icon: Settings },
  { path: "/profile", label: "User Profile", icon: User },
];

export default function DashboardLayout() {
  const navigate = useNavigate();
  const { sidebarOpen, toggleSidebar, searchQuery, setSearchQuery } = useUIStore();
  const { user, isAuthenticated, setUser, logout } = useAuthStore();

  const { data: meData } = useGetMeQuery(undefined, { skip: !isAuthenticated });

  useEffect(() => {
    if (meData) {
      setUser(meData);
    }
  }, [meData, setUser]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };


  return (
    <div className="app-shell flex h-screen w-screen bg-[#0b0f17] text-slate-100 overflow-hidden">
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-20"
        } bg-slate-900/90 backdrop-blur-md border-r border-slate-800 flex flex-col transition-all duration-300 z-30 select-none relative`}
      >
        <div className="h-16 px-4 flex items-center justify-between border-b border-slate-800/80">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="p-2 bg-gradient-to-tr from-violet-600 to-indigo-600 rounded-xl shadow-lg shadow-indigo-500/20 border border-indigo-400/30 flex-shrink-0">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            {sidebarOpen && (
              <div className="flex flex-col">
                <span className="font-bold text-sm tracking-tight text-white">APIRS</span>
                <span className="text-[10px] text-indigo-400 font-medium tracking-wide uppercase">AI Incident Desk</span>
              </div>
            )}
          </div>

          <button
            onClick={toggleSidebar}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>
        </div>

        {sidebarOpen && (
          <div className="mx-3 my-3 p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-glow" />
              <span className="text-xs font-medium text-slate-300">AI Agent Active</span>
            </div>
            <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
              99.98%
            </span>
          </div>
        )}

        <nav className="flex-1 px-3 py-3 space-y-1 overflow-y-auto">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 ${
                    isActive
                      ? "bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-600/20"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                  }`
                }
                title={!sidebarOpen ? item.label : undefined}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {sidebarOpen && <span className="truncate">{item.label}</span>}
                {sidebarOpen && item.badge && (
                  <span className="ml-auto bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[10px] font-bold px-2 py-0.5 rounded-full">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        <div className="p-3 border-t border-slate-800/80 bg-slate-950/40">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center font-bold text-xs text-white flex-shrink-0 shadow-md">
                {user?.full_name ? user.full_name.charAt(0).toUpperCase() : "A"}
              </div>
              {sidebarOpen && (
                <div className="flex flex-col truncate">
                  <span className="text-xs font-semibold text-slate-200 truncate">{user?.full_name || "SRE Lead"}</span>
                  <span className="text-[10px] text-slate-400 truncate">{user?.email || "sre@apirs.ai"}</span>
                </div>
              )}
            </div>

            {sidebarOpen && (
              <button
                onClick={handleLogout}
                title="Log out"
                className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </aside>

      <div className="content-area flex-1 flex flex-col min-w-0 bg-[#0b0f17] overflow-y-auto">
        <header className="h-16 px-6 bg-slate-900/60 backdrop-blur-md border-b border-slate-800 flex items-center justify-between sticky top-0 z-20">
          <div className="relative w-80">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search incidents, logs, services, AI insights..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-950/80 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50"
            />
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-slate-300 font-medium">Cluster: prod-us-east-1</span>
            </div>

            <button className="relative p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors">
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 animate-ping" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500" />
            </button>
          </div>
        </header>

        <main className="p-6 flex-1">
          <Outlet />
        </main>
        <ToastContainer />
      </div>
    </div>
  );
}
