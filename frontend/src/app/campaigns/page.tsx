"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Layers, ArrowRight, Clock, Building2, Users, FileCheck2 } from "lucide-react";
import { CampaignAPI } from "@/lib/api";
import { Campaign } from "@/types";
import { formatDate } from "@/lib/utils";

export default function CampaignsListPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCampaigns() {
      try {
        const data = await CampaignAPI.list();
        setCampaigns(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadCampaigns();
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Outreach Campaigns</h1>
          <p className="text-sm text-slate-400">
            Manage your autonomous prospect discovery and personalization campaigns.
          </p>
        </div>
        <Link
          href="/campaigns/new"
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary hover:bg-primary-hover text-white text-sm font-medium shadow-sm transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Campaign
        </Link>
      </div>

      {loading ? (
        <div className="p-12 text-center text-muted text-sm">Loading campaigns...</div>
      ) : campaigns.length === 0 ? (
        <div className="p-12 rounded-xl bg-surface border border-dashed border-border text-center space-y-3">
          <Layers className="w-8 h-8 text-muted mx-auto" />
          <div className="text-base font-semibold text-white">No campaigns found</div>
          <p className="text-xs text-muted max-w-md mx-auto">
            Define a natural-language outreach objective and let the KORE agent discover companies and craft personalized drafts.
          </p>
          <Link
            href="/campaigns/new"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white text-xs font-medium"
          >
            Create Your First Campaign
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {campaigns.map((camp) => (
            <Link
              key={camp._id}
              href={`/campaigns/${camp._id}`}
              className="p-5 rounded-xl bg-surface hover:bg-surface-card border border-border hover:border-slate-700 transition-all space-y-4 group"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-semibold text-white group-hover:text-primary transition-colors text-base">
                    {camp.name}
                  </h3>
                  <div className="text-xs text-muted flex items-center gap-1.5 mt-1">
                    <Clock className="w-3.5 h-3.5" />
                    {formatDate(camp.createdAt)}
                  </div>
                </div>
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full capitalize font-medium ${
                    camp.status === "completed"
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                      : camp.status === "running"
                      ? "bg-primary/10 text-primary border border-primary/20 animate-pulse"
                      : "bg-slate-800 text-slate-400 border border-slate-700"
                  }`}
                >
                  {camp.status}
                </span>
              </div>

              <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                {camp.objective}
              </p>

              <div className="grid grid-cols-3 gap-2 pt-3 border-t border-border/60 text-center">
                <div className="p-2 rounded-lg bg-surface-card border border-border/40">
                  <div className="text-xs text-muted flex items-center justify-center gap-1">
                    <Building2 className="w-3 h-3 text-blue-400" /> Companies
                  </div>
                  <div className="text-sm font-bold text-white mt-0.5">{camp.companiesCount || 0}</div>
                </div>
                <div className="p-2 rounded-lg bg-surface-card border border-border/40">
                  <div className="text-xs text-muted flex items-center justify-center gap-1">
                    <Users className="w-3 h-3 text-indigo-400" /> Contacts
                  </div>
                  <div className="text-sm font-bold text-white mt-0.5">{camp.contactsCount || 0}</div>
                </div>
                <div className="p-2 rounded-lg bg-surface-card border border-border/40">
                  <div className="text-xs text-muted flex items-center justify-center gap-1">
                    <FileCheck2 className="w-3 h-3 text-amber-400" /> Drafts
                  </div>
                  <div className="text-sm font-bold text-white mt-0.5">{camp.draftsCount || 0}</div>
                </div>
              </div>

              <div className="flex items-center justify-end text-xs text-primary font-medium gap-1 group-hover:translate-x-1 transition-transform">
                <span>View Execution & Prospects</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
