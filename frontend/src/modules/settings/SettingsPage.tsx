import { Bell, Shield, Cpu, Key } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";

const settingsGroups = [
  {
    icon: <Bell className="w-4 h-4 text-amber-400" />,
    title: "Notifications",
    description: "Configure alert channels and notification preferences.",
    items: ["PagerDuty Webhook", "Slack #incident-response", "Email Digest", "SMS Alerts"],
  },
  {
    icon: <Shield className="w-4 h-4 text-emerald-400" />,
    title: "Security",
    description: "Manage API tokens, session policy, and MFA.",
    items: ["API Keys", "Single Sign-On (SSO)", "Multi-Factor Authentication", "Session Timeout"],
  },
  {
    icon: <Cpu className="w-4 h-4 text-violet-400" />,
    title: "AI Configuration",
    description: "Tune AI sensitivity, confidence thresholds, and automation level.",
    items: ["Min Confidence Threshold: 80%", "Auto-execute LOW risk actions", "RAG Knowledge Base Sync", "AI Model Version: GPT-4o"],
  },
  {
    icon: <Key className="w-4 h-4 text-indigo-400" />,
    title: "Integrations",
    description: "Connect third-party tools and monitoring services.",
    items: ["Datadog APM", "PagerDuty", "GitHub", "Jira", "AWS CloudWatch"],
  },
];

export default function SettingsPage() {
  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-50 tracking-tight">Settings</h1>
        <p className="text-sm text-slate-400 mt-0.5">System configuration, integrations, AI tuning, and security preferences</p>
      </div>

      <div className="grid gap-4">
        {settingsGroups.map((group) => (
          <Card key={group.title} className="hover:border-slate-700 transition-colors">
            <CardHeader>
              <CardTitle>
                {group.icon}
                {group.title}
              </CardTitle>
              <Button variant="ghost" size="sm">Configure</Button>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-slate-400 mb-3">{group.description}</p>
              <div className="flex flex-wrap gap-2">
                {group.items.map((item) => (
                  <span key={item} className="inline-flex items-center text-xs px-2.5 py-1 rounded-lg bg-slate-800/60 border border-slate-700/60 text-slate-300">
                    {item}
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
