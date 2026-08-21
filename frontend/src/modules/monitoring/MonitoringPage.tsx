import React from "react";
import { Activity, Cpu, HardDrive, Wifi, Server, Globe } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { AreaChart, Area, ResponsiveContainer } from "recharts";

const generateMetricData = (base: number, variance: number = 10) =>
  Array.from({ length: 12 }, (_, i) => ({
    time: `${(new Date().getHours() - 12 + i + 24) % 24}:00`,
    value: Math.max(0, Math.min(100, base + (Math.random() - 0.5) * variance * 2)),
  }));

const cpuData = generateMetricData(62, 15);
const memData = generateMetricData(74, 8);
const diskData = generateMetricData(45, 3);
const networkInData = generateMetricData(38, 20);

const services = [
  { name: "api-gateway", status: "DEGRADED", region: "us-east-1", latency: 342, errorRate: 2.3, replicas: 4 },
  { name: "auth-service", status: "OPERATIONAL", region: "us-east-1", latency: 18, errorRate: 0.01, replicas: 3 },
  { name: "payment-svc", status: "OPERATIONAL", region: "us-east-1", latency: 56, errorRate: 0.04, replicas: 6 },
  { name: "postgres-primary", status: "OUTAGE", region: "us-east-1", latency: 9999, errorRate: 100, replicas: 1 },
  { name: "redis-cluster", status: "OPERATIONAL", region: "us-east-1", latency: 3, errorRate: 0.0, replicas: 3 },
  { name: "notification-svc", status: "OPERATIONAL", region: "eu-west-1", latency: 34, errorRate: 0.02, replicas: 2 },
];

interface MetricGaugeProps {
  label: string;
  value: number;
  unit?: string;
  color: string;
  icon: React.ReactNode;
  data: Array<{ time: string; value: number }>;
}

function MetricGauge({ label, value, unit = "%", color, icon, data }: MetricGaugeProps) {
  const isWarning = value > 75;
  const isCritical = value > 90;
  const barColor = isCritical ? "#f43f5e" : isWarning ? "#f59e0b" : color;

  return (
    <Card className="hover:border-slate-700 transition-colors">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-slate-800 rounded-lg text-slate-300">{icon}</div>
          <span className="text-xs font-semibold text-slate-300">{label}</span>
        </div>
        <div className="text-right">
          <span className={`text-lg font-bold ${isCritical ? "text-rose-400" : isWarning ? "text-amber-400" : "text-slate-50"}`}>
            {typeof value === "number" ? value.toFixed(1) : value}
          </span>
          <span className="text-xs text-slate-500 ml-0.5">{unit}</span>
        </div>
      </div>
      <div className="h-1.5 bg-slate-800 rounded-full mb-3 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${Math.min(100, value)}%`, backgroundColor: barColor }}
        />
      </div>
      <ResponsiveContainer width="100%" height={50}>
        <AreaChart data={data} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id={`grad-${label}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={barColor} stopOpacity={0.3} />
              <stop offset="95%" stopColor={barColor} stopOpacity={0} />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="value"
            stroke={barColor}
            fill={`url(#grad-${label})`}
            strokeWidth={1.5}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
      <p className="text-[10px] text-slate-500 mt-1 text-right">Last 12 hours</p>
    </Card>
  );
}

export default function MonitoringPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-50 tracking-tight">Production Monitoring</h1>
          <p className="text-sm text-slate-400 mt-0.5">Real-time system health and performance telemetry</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Live · Refreshes every 30s
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricGauge label="CPU Usage" value={62.4} icon={<Cpu className="w-4 h-4" />} color="#6366f1" data={cpuData} />
        <MetricGauge label="Memory Usage" value={74.1} icon={<Activity className="w-4 h-4" />} color="#8b5cf6" data={memData} />
        <MetricGauge label="Disk I/O" value={45.8} icon={<HardDrive className="w-4 h-4" />} color="#06b6d4" data={diskData} />
        <MetricGauge label="Network In" value={38.2} unit=" Mbps" icon={<Wifi className="w-4 h-4" />} color="#10b981" data={networkInData} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            <Globe className="w-4 h-4 text-indigo-400" />
            Service Registry – Health Status
          </CardTitle>
          <span className="text-xs text-slate-400">
            {services.filter((s) => s.status === "OPERATIONAL").length}/{services.length} healthy
          </span>
        </CardHeader>
        <CardContent padding="none">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-950/60 text-slate-400 uppercase text-[11px] font-semibold tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-5 py-3">Service</th>
                  <th className="px-4 py-3">Region</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Latency</th>
                  <th className="px-4 py-3">Error Rate</th>
                  <th className="px-4 py-3">Replicas</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {services.map((svc) => (
                  <tr key={svc.name} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        <Server className="w-3.5 h-3.5 text-slate-500" />
                        <span className="font-mono font-medium text-slate-100">{svc.name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-400 font-mono text-[11px]">{svc.region}</td>
                    <td className="px-4 py-3">
                      <Badge variant="status" status={svc.status as any}>{svc.status}</Badge>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`font-semibold ${svc.latency > 500 ? "text-rose-400" : svc.latency > 100 ? "text-amber-400" : "text-emerald-400"}`}>
                        {svc.latency > 9000 ? "—" : `${svc.latency}ms`}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`font-semibold ${svc.errorRate > 5 ? "text-rose-400" : svc.errorRate > 1 ? "text-amber-400" : "text-emerald-400"}`}>
                        {svc.errorRate === 100 ? "—" : `${svc.errorRate}%`}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-300">{svc.replicas}x</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
