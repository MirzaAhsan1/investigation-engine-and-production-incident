import { useState } from "react";
import { Search, FileText, Tag, ExternalLink } from "lucide-react";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";

const articles = [
  { id: "KB-001", title: "Database Connection Pool Management & Best Practices", category: "Databases", tags: ["postgres", "connection-pool", "performance"], lastUpdated: "2026-07-22", severity: "P0" },
  { id: "KB-002", title: "Kubernetes Pod Restart Loop Debugging Guide", category: "Infrastructure", tags: ["k8s", "pods", "debugging"], lastUpdated: "2026-07-20", severity: "P1" },
  { id: "KB-003", title: "Redis Cache Miss Rate Troubleshooting Runbook", category: "Caching", tags: ["redis", "cache", "performance"], lastUpdated: "2026-07-18", severity: "P2" },
  { id: "KB-004", title: "API Gateway Latency Investigation Playbook", category: "Networking", tags: ["api-gateway", "latency", "nginx"], lastUpdated: "2026-07-15", severity: "P1" },
  { id: "KB-005", title: "Memory Leak Detection & Profiling in Node.js Services", category: "Application", tags: ["nodejs", "memory", "profiling"], lastUpdated: "2026-07-10", severity: "P1" },
  { id: "KB-006", title: "Incident Commander Runbook – P0 Response Protocol", category: "Process", tags: ["incident-response", "protocol", "P0"], lastUpdated: "2026-07-01", severity: "P0" },
];

const categories = ["All", "Databases", "Infrastructure", "Caching", "Networking", "Application", "Process"];

export default function KnowledgeBasePage() {
  const [activeCategory, setActiveCategory] = useState("All");
  const [query, setQuery] = useState("");

  const filtered = articles.filter((a) => {
    const matchesCategory = activeCategory === "All" || a.category === activeCategory;
    const matchesQuery = !query || a.title.toLowerCase().includes(query.toLowerCase()) || a.tags.some((t) => t.includes(query.toLowerCase()));
    return matchesCategory && matchesQuery;
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-50 tracking-tight">Knowledge Base</h1>
        <p className="text-sm text-slate-400 mt-0.5">AI-indexed runbooks, postmortems, and incident response playbooks</p>
      </div>

      <div className="relative">
        <Search className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search runbooks, postmortems, tags..."
          className="w-full pl-10 pr-4 py-3 text-sm bg-slate-900/80 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
        />
      </div>

      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all ${
              activeCategory === cat
                ? "bg-indigo-600 text-white border-indigo-500"
                : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filtered.map((article) => (
          <Card key={article.id} className="hover:border-slate-700 transition-all cursor-pointer group">
            <div className="flex items-start justify-between gap-3">
              <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl flex-shrink-0">
                <FileText className="w-4 h-4 text-indigo-400" />
              </div>
              <ExternalLink className="w-4 h-4 text-slate-600 group-hover:text-slate-400 transition-colors flex-shrink-0 mt-1" />
            </div>
            <div className="mt-3">
              <span className="text-[10px] font-mono text-slate-500">{article.id} · {article.category}</span>
              <h3 className="text-sm font-semibold text-slate-100 mt-1 group-hover:text-indigo-300 transition-colors">{article.title}</h3>
              <div className="flex flex-wrap gap-1.5 mt-2.5">
                {article.tags.map((tag) => (
                  <span key={tag} className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-md bg-slate-800 text-slate-400 border border-slate-700">
                    <Tag className="w-2.5 h-2.5" />{tag}
                  </span>
                ))}
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-500">
              <span>Updated {article.lastUpdated}</span>
              <Badge variant="severity" severity={article.severity as any}>{article.severity} relevance</Badge>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
