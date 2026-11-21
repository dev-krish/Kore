"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Send,
  Users,
  FileCheck2,
  UserCheck,
  Settings,
  Sparkles,
  Layers,
} from "lucide-react";

export function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { label: "Dashboard", href: "/", icon: LayoutDashboard },
    { label: "Campaigns", href: "/campaigns", icon: Layers },
    { label: "Approval Queue", href: "/drafts", icon: FileCheck2 },
    { label: "Student Profile", href: "/profile", icon: UserCheck },
    { label: "Integrations", href: "/integrations", icon: Settings },
  ];

  return (
    <aside className="w-64 min-h-screen bg-surface border-r border-border flex flex-col justify-between shrink-0">
      <div>
        {/* Brand */}
        <div className="h-16 flex items-center px-6 border-b border-border gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary/20 border border-primary/40 flex items-center justify-center text-primary font-bold shadow-glow">
            K
          </div>
          <div>
            <div className="font-bold text-white text-base tracking-wide flex items-center gap-1.5">
              KORE
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary/20 text-primary border border-primary/30 uppercase tracking-wider font-semibold">
                MVP
              </span>
            </div>
            <div className="text-[11px] text-muted font-medium">Outreach Intelligence</div>
          </div>
        </div>

        {/* Navigation */}
        <div className="px-3 py-6 space-y-1">
          <div className="px-3 pb-2 text-[11px] font-semibold text-muted uppercase tracking-wider">
            Platform
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary/15 text-primary border border-primary/30 shadow-sm"
                    : "text-slate-400 hover:text-white hover:bg-surface-hover"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-primary" : "text-slate-400"}`} />
                {item.label}
              </Link>
            );
          })}
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-border">
        <div className="p-3 rounded-lg bg-surface-card border border-border text-xs space-y-1.5">
          <div className="flex items-center justify-between text-slate-300 font-medium">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Agent Active
            </span>
            <span className="text-[10px] text-primary font-mono bg-primary/10 px-1.5 py-0.5 rounded">
              qwen3:4b
            </span>
          </div>
          <p className="text-[11px] text-muted">
            Human Approval Gate strictly enforced on email sending.
          </p>
        </div>
      </div>
    </aside>
  );
}
