import { FileText, Download, Calendar, TrendingUp } from "lucide-react";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";

const reports = [
  { id: "RPT-007", title: "Weekly SRE Report – W29 2026", period: "Jul 14 – Jul 20, 2026", incidents: 14, resolved: 14, mttr: "28m", availability: "99.94%", generatedAt: "2026-07-21 08:00" },
  { id: "RPT-006", title: "Weekly SRE Report – W28 2026", period: "Jul 7 – Jul 13, 2026", incidents: 18, resolved: 16, mttr: "32m", availability: "99.91%", generatedAt: "2026-07-14 08:00" },
  { id: "RPT-005", title: "Monthly Reliability Report – June 2026", period: "Jun 1 – Jun 30, 2026", incidents: 67, resolved: 65, mttr: "38m", availability: "99.87%", generatedAt: "2026-07-01 06:00" },
];

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-50 tracking-tight">Reports</h1>
          <p className="text-sm text-slate-400 mt-0.5">SLA/SLO compliance reports, weekly SRE digests, and incident postmortems</p>
        </div>
        <Button variant="primary" size="sm" leftIcon={<TrendingUp className="w-3.5 h-3.5" />}>
          Generate Report
        </Button>
      </div>

      <div className="grid gap-4">
        {reports.map((report) => (
          <Card key={report.id} className="hover:border-slate-700 transition-colors">
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
                  <FileText className="w-4 h-4 text-indigo-400" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-100">{report.title}</p>
                  <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-1.5">
                    <Calendar className="w-3 h-3" />{report.period}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" leftIcon={<Download className="w-3.5 h-3.5" />}>CSV</Button>
                <Button variant="secondary" size="sm" leftIcon={<Download className="w-3.5 h-3.5" />}>PDF</Button>
              </div>
            </div>

            <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-slate-800/60">
              {[
                { label: "Total Incidents", value: report.incidents },
                { label: "Resolved", value: `${report.resolved}/${report.incidents}` },
                { label: "Avg MTTR", value: report.mttr },
                { label: "Availability", value: report.availability },
              ].map((stat) => (
                <div key={stat.label}>
                  <p className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">{stat.label}</p>
                  <p className="text-sm font-bold text-slate-100 mt-0.5">{stat.value}</p>
                </div>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
