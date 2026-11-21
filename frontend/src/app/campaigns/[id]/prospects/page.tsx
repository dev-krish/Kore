"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Building2,
  Users,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  ArrowLeft,
  Mail,
  Linkedin,
} from "lucide-react";
import { CampaignAPI } from "@/lib/api";
import { Company, Contact } from "@/types";
import { getConfidenceBadgeColor } from "@/lib/utils";

export default function ProspectExplorerPage() {
  const params = useParams();
  const campaignId = params.id as string;

  const [companies, setCompanies] = useState<Company[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [research, setResearch] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadProspects() {
      try {
        const data = await CampaignAPI.getProspects(campaignId);
        setCompanies(data.companies || []);
        setContacts(data.contacts || []);
        setResearch(data.research || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadProspects();
  }, [campaignId]);

  if (loading) {
    return <div className="p-12 text-center text-muted text-sm">Loading prospects...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <Link
            href={`/campaigns/${campaignId}`}
            className="inline-flex items-center gap-1.5 text-xs text-muted hover:text-white transition-colors mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Campaign
          </Link>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Building2 className="w-6 h-6 text-primary" />
            Prospect Explorer
          </h1>
          <p className="text-sm text-slate-400">
            Discovered companies, extracted technical research, and publicly identified leadership contacts.
          </p>
        </div>

        <Link
          href={`/campaigns/${campaignId}/drafts`}
          className="px-4 py-2 rounded-xl bg-primary hover:bg-primary-hover text-white text-xs font-medium shadow-glow transition-all"
        >
          Review Outreach Drafts →
        </Link>
      </div>

      {/* Companies & Contacts Listing */}
      {companies.length === 0 ? (
        <div className="p-12 rounded-xl bg-surface border border-dashed border-border text-center text-sm text-muted">
          No companies discovered for this campaign yet. Run the agent workflow from the campaign page.
        </div>
      ) : (
        <div className="space-y-6">
          {companies.map((company) => {
            const companyContacts = contacts.filter(
              (c) => c.companyName.toLowerCase() === company.name.toLowerCase()
            );
            const companyResearch = research.find(
              (r) => r.companyName.toLowerCase() === company.name.toLowerCase()
            );

            return (
              <div
                key={company._id}
                className="p-6 rounded-2xl bg-surface border border-border space-y-5 shadow-card"
              >
                {/* Company Header */}
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2.5">
                      <h3 className="text-lg font-bold text-white">{company.name}</h3>
                      <a
                        href={company.website}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-primary hover:underline inline-flex items-center gap-1 font-mono"
                      >
                        {company.website.replace("https://", "")}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                    <div className="text-xs text-muted mt-1 flex items-center gap-3">
                      <span>{company.industry}</span>
                      <span>•</span>
                      <span>{company.location}</span>
                    </div>
                  </div>

                  {/* Tech stack badges */}
                  <div className="flex flex-wrap gap-1.5 max-w-md">
                    {company.technologies.map((tech, idx) => (
                      <span
                        key={idx}
                        className="text-[11px] px-2 py-0.5 rounded bg-surface-card border border-border text-slate-300 font-mono"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">{company.description}</p>

                {/* Research Insights Box */}
                {companyResearch && (
                  <div className="p-4 rounded-xl bg-surface-card/60 border border-border/60 text-xs space-y-2">
                    <div className="text-[11px] font-semibold text-primary uppercase tracking-wider flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5" /> Engineering & Internship Fit Analysis
                    </div>
                    <p className="text-slate-300 leading-relaxed font-sans">
                      {companyResearch.researchSummary}
                    </p>
                    <div className="text-[11px] text-muted pt-1">
                      <strong className="text-slate-300">Why Relevant: </strong>
                      {companyResearch.internshipRelevance}
                    </div>
                  </div>
                )}

                {/* Contacts Grid */}
                <div className="space-y-3 pt-2">
                  <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                    <Users className="w-3.5 h-3.5 text-indigo-400" />
                    Identified Leadership & Hiring Contacts ({companyContacts.length})
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {companyContacts.map((contact) => (
                      <div
                        key={contact._id}
                        className="p-4 rounded-xl bg-surface-card border border-border space-y-2.5"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="font-semibold text-white text-sm">{contact.name}</div>
                            <div className="text-xs text-slate-400 font-medium">{contact.role}</div>
                          </div>
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded border font-mono font-medium ${getConfidenceBadgeColor(
                              contact.confidence
                            )}`}
                          >
                            Confidence: {Math.round(contact.confidence * 100)}%
                          </span>
                        </div>

                        {/* Email / Links */}
                        <div className="space-y-1 text-xs">
                          {contact.professionalEmail ? (
                            <div className="flex items-center gap-2 text-slate-300">
                              <Mail className="w-3.5 h-3.5 text-muted shrink-0" />
                              <span className="font-mono text-[11px]">{contact.professionalEmail}</span>
                              <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                {contact.verificationStatus}
                              </span>
                            </div>
                          ) : (
                            <div className="text-[11px] text-amber-400">
                              Email not publicly disclosed. Sourced via leadership page.
                            </div>
                          )}

                          {contact.profileUrl && (
                            <a
                              href={contact.profileUrl}
                              target="_blank"
                              rel="noreferrer"
                              className="text-xs text-primary hover:underline flex items-center gap-1 pt-0.5"
                            >
                              <Linkedin className="w-3 h-3" /> Profile Reference
                              <ExternalLink className="w-2.5 h-2.5" />
                            </a>
                          )}
                        </div>

                        {/* Relevance Score Pill */}
                        {contact.relevanceScore && (
                          <div className="pt-2 border-t border-border/50 flex items-center justify-between text-xs">
                            <span className="text-muted">Relevance Fit:</span>
                            <span className="text-emerald-400 font-bold font-mono">
                              {Math.round(contact.relevanceScore * 100)}% Match
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
