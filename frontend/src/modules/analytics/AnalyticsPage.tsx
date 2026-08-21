import { BarChart3, TrendingUp, Clock, Zap, Calendar } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { MetricCard } from "../../components/ui/MetricCard";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, AreaChart, Area,
} from "recharts";

const incidentTrend = [
  { month: "Feb", incidents: 24, resolved: 22 },
  { month: "Mar", incidents: 18, resolved: 17 },
  { month: "Apr", incidents: 31, resolved: 28 },
  { month: "May", incidents: 14, resolved: 14 },
  { month: "Jun", incidents: 22, resolved: 20 },
  { month: "Jul", incidents: 9, resolved: 6 },
];

const severityDist = [
  { name: "P0 Critical", value: 4, color: "#f43f5e" },
  { name: "P1 High", value: 18, color: "#f97316" },
  { name: "P2 Medium", value: 36, color: "#f59e0b" },
  { name: "P3 Low", value: 60, color: "#06b6d4" },
];

const rootCauses = [
  { cause: "Config Change", count: 31 },
  { cause: "Traffic Surge", count: 24 },
  { cause: "Memory Leak", count: 19 },
  { cause: "Dependency Failure", count: 16 },
  { cause: "Resource Exhaustion", count: 12 },
  { cause: "Human Error", count: 8 },
];

const mttrTrend = [
  { week: "W1", mttr: 58 },
  { week: "W2", mttr: 45 },
  { week: "W3", mttr: 39 },
  { week: "W4", mttr: 32 },
  { week: "W5", mttr: 28 },
  { week: "W6", mttr: 24 },
];

const TOOLTIP_STYLE = {
  contentStyle: { background: "#111827", border: "1px solid #1f2937", borderRadius: 8, fontSize: 12 },
  labelStyle: { color: "#f9fafb" },
};

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-50 tracking-tight">Reliability Analytics</h1>
        <p className="text-sm text-slate-400 mt-0.5">SLO/SLA reporting, MTTR trends, and AI performance metrics</p>
      </div>

      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricCard title="Avg MTTR" value="24m" change="-34% vs last month" changeType="increase" icon={<Clock className="w-5 h-5 text-amber-400" />} statusColor="amber" subtitle="Target: < 30m" />
        <MetricCard title="Avg MTBF" value="192h" change="+12h vs last month" changeType="increase" icon={<TrendingUp className="w-5 h-5 text-emerald-400" />} statusColor="emerald" subtitle="Mean time between failures" />
        <MetricCard title="AI Precision" value="94.7%" change="+1.2% vs last month" changeType="increase" icon={<Zap className="w-5 h-5 text-violet-400" />} statusColor="indigo" subtitle="Root cause detection" />
        <MetricCard title="Availability" value="99.91%" change="-0.05% vs SLO" changeType="neutral" icon={<BarChart3 className="w-5 h-5 text-cyan-400" />} statusColor="cyan" subtitle="SLO target: 99.95%" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <Card>
          <CardHeader>
            <CardTitle><Calendar className="w-4 h-4 text-indigo-400" />Incident Volume – Last 6 Months</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={incidentTrend} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={false} tickLine={false} />
                <Tooltip {...TOOLTIP_STYLE} />
                <Bar dataKey="incidents" name="Total" fill="#6366f1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="resolved" name="Resolved" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Severity Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={severityDist} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={3} dataKey="value">
                  {severityDist.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="transparent" />
                  ))}
                </Pie>
                <Tooltip {...TOOLTIP_STYLE} />
                <Legend
                  formatter={(value) => <span style={{ color: "#94a3b8", fontSize: 11 }}>{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <Card>
          <CardHeader>
            <CardTitle><Clock className="w-4 h-4 text-amber-400" />MTTR Trend – Last 6 Weeks</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={180}>
              <AreaChart data={mttrTrend} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                <defs>
                  <linearGradient id="mttrGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis dataKey="week" tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={false} tickLine={false} />
                <YAxis unit="m" tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={false} tickLine={false} />
                <Tooltip {...TOOLTIP_STYLE} />
                <Area type="monotone" dataKey="mttr" name="MTTR (min)" stroke="#f59e0b" fill="url(#mttrGrad)" strokeWidth={2} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Root Causes</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={rootCauses} layout="vertical" margin={{ top: 0, right: 0, bottom: 0, left: 100 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={false} tickLine={false} />
                <YAxis dataKey="cause" type="category" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} width={100} />
                <Tooltip {...TOOLTIP_STYLE} />
                <Bar dataKey="count" name="Incidents" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
