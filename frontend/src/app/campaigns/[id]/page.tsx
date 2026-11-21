"use client";

import React, { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  Layers,
  Bot,
  Play,
  RotateCcw,
  CheckCircle2,
  Clock,
  AlertCircle,
  Building2,
  Users,
  FileCheck2,
  ExternalLink,
  ChevronRight,
  Sparkles,
  Terminal,
  ShieldAlert,
} from "lucide-react";
import { CampaignAPI, ExecutionAPI } from "@/lib/api";
import { Campaign, AgentExecution, AgentStep, ToolCall } from "@/types";
import { formatDate } from "@/lib/utils";

export default function CampaignDetailPage() {
  const params = useParams();
  const router = useRouter();
  const campaignId = params.id as string;

  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [execution, setExecution] = useState<AgentExecution | null>(null);
  const [liveEvents, setLiveEvents] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<"timeline" | "tools" | "overview">("timeline");
  const [isExecuting, setIsExecuting] = useState(false);
  const [loading, setLoading] = useState(true);

  const eventSourceRef = useRef<EventSource | null>(null);

  // Load Campaign and Execution
  async function loadData() {
    try {
      const [cData, eData] = await Promise.all([
        CampaignAPI.getById(campaignId),
        ExecutionAPI.getLatestForCampaign(campaignId),
      ]);
      setCampaign(cData);
      setExecution(eData);
      if (cData.status === "running") {
        setIsExecuting(true);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, [campaignId]);

  // Connect to Server-Sent Events (SSE)
  useEffect(() => {
    const sseUrl = `http://localhost:8000/api/executions/${campaignId}/events`;
    const es = new EventSource(sseUrl);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setLiveEvents((prev) => [parsed, ...prev]);

        if (parsed.type === "execution_started") {
          setIsExecuting(true);
        } else if (parsed.type === "execution_completed" || parsed.type === "execution_failed") {
          setIsExecuting(false);
          loadData();
        }
      } catch (err) {
        // Heartbeat or malformed
      }
    };

    return () => {
      es.close();
    };
  }, [campaignId]);

  async function handleRerunAgent() {
    setIsExecuting(true);
    try {
      await CampaignAPI.execute(campaignId);
      loadData();
    } catch (err) {
      console.error(err);
      setIsExecuting(false);
    }
  }

  if (loading) {
    return <div className="p-12 text-center text-muted text-sm">Loading campaign details...</div>;
  }

  if (!campaign) {
    return <div className="p-12 text-center text-destructive text-sm">Campaign not found.</div>;
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="p-6 rounded-2xl bg-surface border border-border space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white">{campaign.name}</h1>
              <span
                className={`text-[11px] px-2.5 py-0.5 rounded-full capitalize font-medium ${
                  campaign.status === "completed"
                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    : isExecuting || campaign.status === "running"
                    ? "bg-primary/10 text-primary border border-primary/20 animate-pulse"
                    : "bg-slate-800 text-slate-400 border border-slate-700"
                }`}
              >
                {isExecuting ? "Agent Executing..." : campaign.status}
              </span>
            </div>
            <p className="text-xs text-slate-400 max-w-2xl">{campaign.objective}</p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={handleRerunAgent}
              disabled={isExecuting}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-surface-card hover:bg-surface-hover border border-border text-xs font-medium text-slate-200 transition-colors disabled:opacity-50"
            >
              <RotateCcw className={`w-3.5 h-3.5 ${isExecuting ? "animate-spin" : ""}`} />
              {isExecuting ? "Agent Running..." : "Rerun Agent Workflow"}
            </button>
            <Link
              href={`/campaigns/${campaignId}/drafts`}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary hover:bg-primary-hover text-white text-xs font-medium shadow-glow transition-all"
            >
              <FileCheck2 className="w-3.5 h-3.5" />
              Review Drafts ({campaign.draftsCount || 0})
            </Link>
          </div>
        </div>

        {/* Quick Stats Pill Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-3 border-t border-border">
          <Link
            href={`/campaigns/${campaignId}/prospects`}
            className="p-3 rounded-xl bg-surface-card hover:bg-surface-hover border border-border transition-colors flex items-center justify-between"
          >
            <div>
              <div className="text-[11px] text-muted flex items-center gap-1.5">
                <Building2 className="w-3 h-3 text-blue-400" /> Discovered Companies
              </div>
              <div className="text-lg font-bold text-white mt-0.5">{campaign.companiesCount || 0}</div>
            </div>
            <ChevronRight className="w-4 h-4 text-muted" />
          </Link>

          <Link
            href={`/campaigns/${campaignId}/prospects`}
            className="p-3 rounded-xl bg-surface-card hover:bg-surface-hover border border-border transition-colors flex items-center justify-between"
          >
            <div>
              <div className="text-[11px] text-muted flex items-center gap-1.5">
                <Users className="w-3 h-3 text-indigo-400" /> Sourced Contacts
              </div>
              <div className="text-lg font-bold text-white mt-0.5">{campaign.contactsCount || 0}</div>
            </div>
            <ChevronRight className="w-4 h-4 text-muted" />
          </Link>

          <Link
            href={`/campaigns/${campaignId}/drafts`}
            className="p-3 rounded-xl bg-surface-card hover:bg-surface-hover border border-border transition-colors flex items-center justify-between"
          >
            <div>
              <div className="text-[11px] text-muted flex items-center gap-1.5">
                <FileCheck2 className="w-3 h-3 text-amber-400" /> Prepared Drafts
              </div>
              <div className="text-lg font-bold text-amber-400 mt-0.5">{campaign.draftsCount || 0}</div>
            </div>
            <ChevronRight className="w-4 h-4 text-muted" />
          </Link>

          <div className="p-3 rounded-xl bg-surface-card border border-border flex items-center justify-between">
            <div>
              <div className="text-[11px] text-muted flex items-center gap-1.5">
                <Clock className="w-3 h-3 text-emerald-400" /> Emails Sent
              </div>
              <div className="text-lg font-bold text-emerald-400 mt-0.5">{campaign.emailsSentCount || 0}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-border pb-3">
        <button
          onClick={() => setActiveTab("timeline")}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            activeTab === "timeline"
              ? "bg-primary/15 text-primary border border-primary/30"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Agent Execution Timeline
        </button>
        <button
          onClick={() => setActiveTab("tools")}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            activeTab === "tools"
              ? "bg-primary/15 text-primary border border-primary/30"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Tool Invocations & Observability ({execution?.toolCalls?.length || 0})
        </button>
        <Link
          href={`/campaigns/${campaignId}/prospects`}
          className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition-colors"
        >
          Prospect Explorer →
        </Link>
        <Link
          href={`/campaigns/${campaignId}/drafts`}
          className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition-colors"
        >
          Email Drafts & Approval →
        </Link>
      </div>

      {/* Tab: Timeline */}
      {activeTab === "timeline" && (
        <div className="space-y-4">
          {/* Active Live Indicator */}
          {isExecuting && (
            <div className="p-4 rounded-xl bg-primary/10 border border-primary/30 flex items-center gap-3 text-xs text-primary font-medium animate-pulse">
              <Bot className="w-4 h-4 animate-spin" />
              <span>Agent is actively executing tasks and reasoning via Ollama qwen3:4b...</span>
            </div>
          )}

          {/* Execution Steps */}
          {execution && execution.steps && execution.steps.length > 0 ? (
            <div className="space-y-4">
              {execution.steps.map((step, idx) => (
                <div
                  key={idx}
                  className="p-5 rounded-xl bg-surface border border-border space-y-3 relative overflow-hidden"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-primary/20 text-primary border border-primary/40 flex items-center justify-center text-xs font-bold font-mono">
                        {step.stepNumber}
                      </div>
                      <h4 className="text-sm font-semibold text-white">{step.task}</h4>
                    </div>
                    <span className="text-[11px] text-muted font-mono">{formatDate(step.timestamp)}</span>
                  </div>

                  <div className="p-3 rounded-lg bg-surface-card border border-border/60 text-xs space-y-1.5">
                    <div className="text-[11px] font-semibold text-primary uppercase tracking-wider flex items-center gap-1">
                      <Sparkles className="w-3 h-3" /> Agent Thought & Reasoning
                    </div>
                    <p className="text-slate-300 leading-relaxed font-sans">{step.thought}</p>
                  </div>

                  {step.observation && (
                    <div className="p-3 rounded-lg bg-[#0a1120] border border-border/80 text-xs space-y-1">
                      <div className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> Observation & Finding
                      </div>
                      <p className="text-slate-300 leading-relaxed font-sans">{step.observation}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 rounded-xl bg-surface border border-dashed border-border text-center text-xs text-muted">
              No execution steps recorded yet. Click &quot;Rerun Agent Workflow&quot; to begin.
            </div>
          )}
        </div>
      )}

      {/* Tab: Tool Invocations */}
      {activeTab === "tools" && (
        <div className="space-y-3">
          {execution && execution.toolCalls && execution.toolCalls.length > 0 ? (
            execution.toolCalls.map((tc, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-surface border border-border space-y-2 font-mono text-xs"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Terminal className="w-3.5 h-3.5 text-primary" />
                    <span className="font-bold text-white">{tc.toolName}</span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded font-sans ${
                        tc.isSuccess
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                          : "bg-destructive/10 text-destructive border border-destructive/30"
                      }`}
                    >
                      {tc.isSuccess ? "Success" : "Failed"}
                    </span>
                  </div>
                  <span className="text-[10px] text-muted">{formatDate(tc.timestamp)}</span>
                </div>

                <div className="p-2.5 rounded bg-surface-card border border-border/60 text-slate-300 overflow-x-auto">
                  <span className="text-muted text-[10px]">ARGS: </span>
                  {JSON.stringify(tc.inputArgs)}
                </div>

                {tc.outputSummary && (
                  <div className="text-slate-400 text-xs font-sans">
                    <strong className="text-slate-300">Result: </strong> {tc.outputSummary}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="p-12 rounded-xl bg-surface border border-dashed border-border text-center text-xs text-muted">
              No tool calls logged yet.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
