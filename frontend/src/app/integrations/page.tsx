"use client";

import React, { useEffect, useState } from "react";
import { Settings, CheckCircle2, AlertCircle, Bot, Globe, Mail, ShieldCheck, RefreshCw } from "lucide-react";
import { IntegrationsAPI } from "@/lib/api";

export default function IntegrationsPage() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  async function loadStatus() {
    setLoading(true);
    try {
      const data = await IntegrationsAPI.getStatus();
      setStatus(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadStatus();
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Settings className="w-6 h-6 text-primary" />
            Integration Settings & Health
          </h1>
          <p className="text-sm text-slate-400">
            Monitor the status of local LLM inference, search data providers, and Gmail delivery authorization.
          </p>
        </div>

        <button
          onClick={loadStatus}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface border border-border text-xs text-slate-300 hover:text-white transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} /> Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {/* Ollama Local LLM */}
        <div className="p-6 rounded-2xl bg-surface border border-border space-y-3 shadow-card">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 text-primary flex items-center justify-center">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-semibold text-white text-base">Ollama Local Inference</h3>
                <div className="text-xs text-muted">Configured Model: {status?.ollama?.model || "qwen3:4b"}</div>
              </div>
            </div>

            <span
              className={`text-xs px-2.5 py-0.5 rounded-full font-medium inline-flex items-center gap-1.5 ${
                status?.ollama?.connected
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  : "bg-destructive/10 text-destructive border border-destructive/20"
              }`}
            >
              {status?.ollama?.connected ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
              {status?.ollama?.connected ? "Operational" : "Unreachable"}
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            KORE connects to your local Ollama instance at <code className="text-primary font-mono">{status?.ollama?.baseUrl || "http://localhost:11434"}</code>. All model reasoning, structured JSON parsing, and personalization are computed locally.
          </p>
        </div>

        {/* Company & Contact Discovery Provider */}
        <div className="p-6 rounded-2xl bg-surface border border-border space-y-3 shadow-card">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center">
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-semibold text-white text-base">Discovery & Search Provider</h3>
                <div className="text-xs text-muted">
                  Provider Mode: {status?.search?.isDemoMode ? "Curated Verified Dataset" : "Live Web API"}
                </div>
              </div>
            </div>

            <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 inline-flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5" /> Active
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            KORE uses a provider adapter architecture. When external search API keys (SerpAPI or Tavily) are unconfigured, KORE transparently utilizes a deterministic, verified dataset containing actual Indian AI startups (Sarvam AI, SigNoz, Krutrim, Hasura, Postman) and leadership contacts.
          </p>
        </div>

        {/* Gmail OAuth 2.0 Integration */}
        <div className="p-6 rounded-2xl bg-surface border border-border space-y-3 shadow-card">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
                <Mail className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-semibold text-white text-base">Gmail API (OAuth 2.0)</h3>
                <div className="text-xs text-muted">
                  {status?.gmail?.configured ? "Google Client Credentials Loaded" : "Running in Verified Demo Delivery Mode"}
                </div>
              </div>
            </div>

            <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 inline-flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              {status?.gmail?.configured ? "Ready for OAuth" : "Demo Mode Active"}
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            Email sending requires explicit student approval per draft. In Demo Mode, approvals are verified via cryptographic SHA-256 integrity checks, and delivery records with provider message IDs are generated and logged.
          </p>
        </div>
      </div>
    </div>
  );
}
