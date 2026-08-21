import { User, Mail, Calendar, Shield, LogOut } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { useGetMeQuery } from "../../api/authApi";
import useAuthStore from "../../store/authStore";
import { useNavigate } from "react-router-dom";
import { Skeleton } from "../../components/ui/Skeleton";

export default function ProfilePage() {
  const { data: user, isLoading } = useGetMeQuery();
  const { logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-50 tracking-tight">User Profile</h1>
        <p className="text-sm text-slate-400 mt-0.5">Account information, credentials, and session management</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle><User className="w-4 h-4 text-indigo-400" />Account Details</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              <Skeleton height="h-10" />
              <Skeleton height="h-10" />
              <Skeleton height="h-10" width="w-1/2" />
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-4 p-4 bg-slate-950/60 rounded-xl border border-slate-800/60">
                <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center text-xl font-bold text-white shadow-lg">
                  {user?.full_name?.charAt(0) ?? "A"}
                </div>
                <div>
                  <p className="text-sm font-bold text-slate-100">{user?.full_name ?? "SRE Engineer"}</p>
                  <p className="text-xs text-indigo-400 font-medium mt-0.5">Site Reliability Engineer</p>
                  <p className="text-xs text-emerald-400 mt-0.5 flex items-center gap-1.5">
                    <Shield className="w-3 h-3" /> Active session
                  </p>
                </div>
              </div>

              {[
                { icon: <User className="w-4 h-4 text-slate-500" />, label: "Full Name", value: user?.full_name ?? "—" },
                { icon: <Mail className="w-4 h-4 text-slate-500" />, label: "Email Address", value: user?.email ?? "—" },
                { icon: <Calendar className="w-4 h-4 text-slate-500" />, label: "Member Since", value: user?.created_at ? new Date(user.created_at).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" }) : "—" },
              ].map((field) => (
                <div key={field.label} className="flex items-center gap-3 px-4 py-3 bg-slate-950/40 rounded-xl border border-slate-800/60">
                  {field.icon}
                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">{field.label}</p>
                    <p className="text-sm text-slate-100 mt-0.5 font-medium">{field.value}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle><Shield className="w-4 h-4 text-rose-400" />Danger Zone</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 bg-rose-500/5 border border-rose-500/20 rounded-xl">
            <div>
              <p className="text-sm font-semibold text-slate-100">Sign out of APIRS</p>
              <p className="text-xs text-slate-400 mt-0.5">This will clear your session and JWT token from this device.</p>
            </div>
            <Button variant="danger" size="sm" onClick={handleLogout} leftIcon={<LogOut className="w-3.5 h-3.5" />}>
              Sign Out
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
