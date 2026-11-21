"use client";

import Link from "next/link";
import { Plus, Bot, ShieldCheck } from "lucide-react";

export function Header() {
  return (
    <header className="h-16 border-b border-border bg-surface/50 backdrop-blur px-8 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-4">
        <div className="text-xs text-muted font-medium flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-surface-card border border-border text-slate-300">
            Autonomous Professional Outreach
          </span>
          <span>•</span>
          <span className="text-emerald-400 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" /> Human-in-the-Loop Safe
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Link
          href="/campaigns/new"
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-medium shadow-sm transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          New Campaign
        </Link>
      </div>
    </header>
  );
}
