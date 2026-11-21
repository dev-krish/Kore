"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Layers,
  Building2,
  Users,
  FileCheck2,
  MailCheck,
  ArrowRight,
  Sparkles,
  Bot,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import { CampaignAPI, DraftAPI, IntegrationsAPI } from "@/lib/api";
import { Campaign, EmailDraft } from "@/types";
import { formatDate } from "@/lib/utils";

export default function DashboardPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [drafts, setDrafts] = useState<EmailDraft[]>([]);
  const [integrations, setIntegrations] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [cList, dList, intg] = await Promise.all([
          CampaignAPI.list(),
          DraftAPI.list(),
          IntegrationsAPI.getStatus(),
        ]);
        setCampaigns(cList);
        setDrafts(dList);
        setIntegrations(intg);
      } catch (err) {
        console.error("Dashboard data load error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const totalCompanies = campaigns.reduce((acc, c) => acc + (c.companiesCount || 0), 0);
  const totalContacts = campaigns.reduce((acc, c) => acc + (c.contactsCount || 0), 0);
  const pendingApprovals = drafts.filter(
    (d) => d.approvalStatus === "generated" || d.approvalStatus === "pending_review"
  ).length;
  const emailsSent = campaigns.reduce((acc, c) => acc + (c.emailsSentCount || 0), 0);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Hero Welcome */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-surface to-surface-card border border-border shadow-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5" />
            Autonomous Outreach Intelligence
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Welcome to KORE
          </h1>
          <p className="text-sm text-slate-400 max-w-xl">
            Turn your career profile into research-backed, verified prospect discovery and personalized, human-approved outreach.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/campaigns/new"
            className="px-4 py-2.5 rounded-xl bg-primary hover:bg-primary-hover text-white text-sm font-medium shadow-glow transition-all flex items-center gap-2"
          >
            <Bot className="w-4 h-4" />
            Create Campaign
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="p-4 rounded-xl bg-surface border border-border space-y-1">
          <div className="text-xs text-muted font-medium flex items-center justify-between">
            Campaigns
            <Layers className="w-3.5 h-3.5 text-primary" />
          </div>
          <div className="text-2xl font-bold text-white">{campaigns.length}</div>
          <div className="text-[11px] text-slate-500">Active workflows</div>
        </div>

        <div className="p-4 rounded-xl bg-surface border border-border space-y-1">
          <div className="text-xs text-muted font-medium flex items-center justify-between">
            Companies
            <Building2 className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white">{totalCompanies}</div>
          <div className="text-[11px] text-slate-500">Researched & verified</div>
        </div>

        <div className="p-4 rounded-xl bg-surface border border-border space-y-1">
          <div className="text-xs text-muted font-medium flex items-center justify-between">
            Contacts
            <Users className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">{totalContacts}</div>
          <div className="text-[11px] text-slate-500">Founders & Leadership</div>
        </div>

        <div className="p-4 rounded-xl bg-surface border border-border space-y-1">
          <div className="text-xs text-muted font-medium flex items-center justify-between">
            Pending Approval
            <FileCheck2 className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400">{pendingApprovals}</div>
          <div className="text-[11px] text-slate-500">Awaiting your review</div>
        </div>

        <div className="p-4 rounded-xl bg-surface border border-border space-y-1">
          <div className="text-xs text-muted font-medium flex items-center justify-between">
            Emails Sent
            <MailCheck className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">{emailsSent}</div>
          <div className="text-[11px] text-slate-500">Human-approved sends</div>
        </div>
      </div>

      {/* Main Grid: Active Campaigns + System Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Recent Campaigns */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              Recent Outreach Campaigns
            </h2>
            <Link
              href="/campaigns"
              className="text-xs text-primary hover:underline flex items-center gap-1"
            >
              View all ({campaigns.length})
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {campaigns.length === 0 ? (
            <div className="p-8 rounded-xl bg-surface border border-dashed border-border text-center space-y-3">
              <div className="w-10 h-10 rounded-full bg-primary/10 text-primary mx-auto flex items-center justify-center">
                <Layers className="w-5 h-5" />
              </div>
              <div className="text-sm font-medium text-slate-300">No campaigns launched yet</div>
              <p className="text-xs text-muted max-w-sm mx-auto">
                Create your first outreach campaign to begin autonomous discovery of companies and contacts.
              </p>
              <Link
                href="/campaigns/new"
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-medium"
              >
                Launch First Campaign
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {campaigns.slice(0, 4).map((camp) => (
                <Link
                  key={camp._id}
                  href={`/campaigns/${camp._id}`}
                  className="block p-4 rounded-xl bg-surface hover:bg-surface-card border border-border transition-all hover:border-slate-700 space-y-2 group"
                >
                  <div className="flex items-center justify-between">
                    <div className="font-semibold text-white group-hover:text-primary transition-colors text-sm">
                      {camp.name}
                    </div>
                    <span
                      className={`text-[11px] px-2 py-0.5 rounded-full capitalize font-medium ${
                        camp.status === "completed"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : camp.status === "running"
                          ? "bg-primary/10 text-primary border border-primary/20 animate-pulse"
                          : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {camp.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-1">{camp.objective}</p>
                  <div className="flex items-center gap-4 text-[11px] text-muted pt-1 border-t border-border/50">
                    <span>{camp.companiesCount || 0} companies</span>
                    <span>•</span>
                    <span>{camp.contactsCount || 0} contacts</span>
                    <span>•</span>
                    <span>{camp.draftsCount || 0} drafts</span>
                    <span className="ml-auto">{formatDate(camp.createdAt)}</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Platform Services & Approval Guard */}
        <div className="space-y-6">
          {/* Approval Guard Box */}
          <div className="p-5 rounded-xl bg-surface border border-border space-y-3">
            <div className="flex items-center gap-2 text-white font-semibold text-sm">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Human Approval Guarantee
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              KORE strictly forbids automatic mass-mailing. Every generated email requires explicit human approval with cryptographic SHA-256 integrity validation.
            </p>
            <Link
              href="/drafts"
              className="inline-flex items-center gap-2 text-xs text-primary font-medium hover:underline pt-1"
            >
              Open Approval Queue ({pendingApprovals})
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* System Services Status */}
          <div className="p-5 rounded-xl bg-surface border border-border space-y-4">
            <div className="text-sm font-semibold text-white flex items-center justify-between">
              <span>Platform Integrations</span>
              <Link href="/integrations" className="text-xs text-muted hover:text-white">
                Manage
              </Link>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300">Ollama Local LLM</span>
                <span className="inline-flex items-center gap-1.5 text-emerald-400 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {integrations?.ollama?.model || "qwen3:4b"}
                </span>
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300">Search Provider</span>
                <span className="inline-flex items-center gap-1.5 text-blue-400 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {integrations?.search?.provider === "demo" ? "Curated Demo Dataset" : "Live API"}
                </span>
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300">Gmail OAuth 2.0</span>
                <span className="inline-flex items-center gap-1.5 text-indigo-400 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {integrations?.gmail?.configured ? "Connected" : "Simulated Demo Mode"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
