"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Bot, Sparkles, ArrowRight, ShieldCheck, Check } from "lucide-react";
import { CampaignAPI } from "@/lib/api";

export default function NewCampaignPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [name, setName] = useState("India AI Startups - Summer Internship 2025");
  const [objective, setObjective] = useState(
    "Find 5 early-stage AI startups in India that may be suitable for a computer science student interested in AI engineering and full-stack development. Identify founders or engineering hiring contacts, research their companies and prepare personalized internship outreach emails."
  );
  const [targetIndustry, setTargetIndustry] = useState("AI & Software Startups");
  const [targetLocation, setTargetLocation] = useState("Bengaluru, India / Remote");
  const [targetRoles, setTargetRoles] = useState(
    "Founder, Co-Founder, CTO, Head of Engineering, Engineering Manager"
  );
  const [targetProspectCount, setTargetProspectCount] = useState(5);
  const [preferredTechnologies, setPreferredTechnologies] = useState(
    "Python, PyTorch, FastAPI, Next.js, LLMs"
  );

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim() || !objective.trim()) {
      setError("Please provide a campaign name and objective.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const created = await CampaignAPI.create({
        name,
        objective,
        targetIndustry,
        targetLocation,
        targetRoles: targetRoles.split(",").map((r) => r.trim()).filter(Boolean),
        targetProspectCount: Number(targetProspectCount),
        preferredTechnologies: preferredTechnologies.split(",").map((t) => t.trim()).filter(Boolean),
      });

      // Automatically trigger agent execution workflow
      await CampaignAPI.execute(created._id);

      // Redirect immediately to live execution timeline
      router.push(`/campaigns/${created._id}`);
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.detail || "Failed to create and launch campaign.");
      setLoading(false);
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Bot className="w-6 h-6 text-primary" />
          Create New Campaign
        </h1>
        <p className="text-sm text-slate-400">
          State your outreach objective in plain English. The KORE agent will parse tasks, discover companies, and prepare personalized drafts.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="p-6 rounded-2xl bg-surface border border-border shadow-card space-y-6">
        {/* Campaign Name */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-slate-300">
            Campaign Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary transition-colors"
            placeholder="e.g., Summer 2025 AI Engineering Outreach"
            required
          />
        </div>

        {/* Natural Language Objective */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
            <span>Natural-Language Outreach Objective</span>
            <span className="text-[11px] text-primary flex items-center gap-1 font-normal">
              <Sparkles className="w-3 h-3" /> Core Agent Prompt
            </span>
          </label>
          <textarea
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            rows={4}
            className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary transition-colors leading-relaxed"
            placeholder="Describe your desired target companies, roles, and goal..."
            required
          />
          <p className="text-[11px] text-muted">
            The Agent Planner breaks this prompt down into concrete discovery, scraping, contact extraction, and drafting tasks.
          </p>
        </div>

        {/* Configuration Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              Target Industry
            </label>
            <input
              type="text"
              value={targetIndustry}
              onChange={(e) => setTargetIndustry(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary transition-colors"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              Target Location
            </label>
            <input
              type="text"
              value={targetLocation}
              onChange={(e) => setTargetLocation(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary transition-colors"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              Target Roles (comma-separated)
            </label>
            <input
              type="text"
              value={targetRoles}
              onChange={(e) => setTargetRoles(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary transition-colors"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              Prospect Count Target (1 - 10)
            </label>
            <input
              type="number"
              min={1}
              max={10}
              value={targetProspectCount}
              onChange={(e) => setTargetProspectCount(Number(e.target.value))}
              className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary transition-colors"
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-slate-300">
            Preferred Technologies & Keywords
          </label>
          <input
            type="text"
            value={preferredTechnologies}
            onChange={(e) => setPreferredTechnologies(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary transition-colors"
          />
        </div>

        {/* Safety Note */}
        <div className="p-3.5 rounded-xl bg-surface-card/60 border border-border flex items-start gap-3 text-xs text-slate-400">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          <span>
            Launching this campaign will run discovery, research, and draft preparation.
            <strong className="text-slate-200"> No emails will ever be dispatched</strong> without your explicit, cryptographic review and approval.
          </span>
        </div>

        {/* Submit Button */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={() => router.back()}
            className="px-4 py-2.5 rounded-xl bg-surface-card hover:bg-surface-hover text-slate-300 text-sm font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-primary hover:bg-primary-hover disabled:opacity-50 text-white text-sm font-medium shadow-glow flex items-center gap-2 transition-all"
          >
            {loading ? "Initializing Agent Pipeline..." : "Launch Agent Pipeline"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
