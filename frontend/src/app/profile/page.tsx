"use client";

import React, { useEffect, useState } from "react";
import { UserCheck, Save, Plus, Trash2, CheckCircle2, Sparkles } from "lucide-react";
import { ProfileAPI } from "@/lib/api";
import { StudentProfile, ProjectItem } from "@/types";

export default function ProfilePage() {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await ProfileAPI.getMe();
        setProfile(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!profile) return;
    setSaving(true);
    setSuccessMessage(false);
    try {
      const updated = await ProfileAPI.updateMe(profile);
      setProfile(updated);
      setSuccessMessage(true);
      setTimeout(() => setSuccessMessage(false), 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  }

  function addProject() {
    if (!profile) return;
    const newProj: ProjectItem = {
      title: "New Technical Project",
      description: "Description of your architecture, technologies, and achievements.",
      technologies: ["Python", "FastAPI"],
    };
    setProfile({
      ...profile,
      projects: [...(profile.projects || []), newProj],
    });
  }

  function removeProject(index: number) {
    if (!profile) return;
    const updated = [...profile.projects];
    updated.splice(index, 1);
    setProfile({ ...profile, projects: updated });
  }

  if (loading) {
    return <div className="p-12 text-center text-muted text-sm">Loading student profile...</div>;
  }

  if (!profile) {
    return <div className="p-12 text-center text-destructive text-sm">Unable to load profile.</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <UserCheck className="w-6 h-6 text-primary" />
            Student Career Profile
          </h1>
          <p className="text-sm text-slate-400">
            This profile is directly used by the KORE agent to evaluate relevance and write personalized outreach.
          </p>
        </div>

        {successMessage && (
          <div className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
            <CheckCircle2 className="w-4 h-4" /> Profile saved successfully!
          </div>
        )}
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Education & Bio */}
        <div className="p-6 rounded-2xl bg-surface border border-border shadow-card space-y-4">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
            Academic Background
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Full Name</label>
              <input
                type="text"
                value={profile.fullName || ""}
                onChange={(e) => setProfile({ ...profile, fullName: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">University / College</label>
              <input
                type="text"
                value={profile.college || ""}
                onChange={(e) => setProfile({ ...profile, college: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Degree & Branch</label>
              <input
                type="text"
                value={profile.degree || ""}
                onChange={(e) => setProfile({ ...profile, degree: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Current Academic Year</label>
              <input
                type="text"
                value={profile.currentYear || ""}
                onChange={(e) => setProfile({ ...profile, currentYear: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary"
                placeholder="e.g. 3rd Year"
                required
              />
            </div>
          </div>
        </div>

        {/* Technical Skills */}
        <div className="p-6 rounded-2xl bg-surface border border-border shadow-card space-y-4">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
            Technical Stack & Skills
          </h3>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              Programming Languages (comma-separated)
            </label>
            <input
              type="text"
              value={profile.programmingLanguages?.join(", ") || ""}
              onChange={(e) =>
                setProfile({
                  ...profile,
                  programmingLanguages: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                })
              }
              className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              Frameworks & Tools (comma-separated)
            </label>
            <input
              type="text"
              value={profile.frameworks?.join(", ") || ""}
              onChange={(e) =>
                setProfile({
                  ...profile,
                  frameworks: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                })
              }
              className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">GitHub Profile</label>
              <input
                type="text"
                value={profile.githubProfile || ""}
                onChange={(e) => setProfile({ ...profile, githubProfile: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">LinkedIn Profile</label>
              <input
                type="text"
                value={profile.linkedinProfile || ""}
                onChange={(e) => setProfile({ ...profile, linkedinProfile: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Portfolio URL</label>
              <input
                type="text"
                value={profile.portfolioUrl || ""}
                onChange={(e) => setProfile({ ...profile, portfolioUrl: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-surface-card border border-border text-white text-sm focus:outline-none focus:border-primary"
              />
            </div>
          </div>
        </div>

        {/* Projects */}
        <div className="p-6 rounded-2xl bg-surface border border-border shadow-card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
              Highlighted Projects
            </h3>
            <button
              type="button"
              onClick={addProject}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-card hover:bg-surface-hover border border-border text-xs text-primary font-medium"
            >
              <Plus className="w-3.5 h-3.5" /> Add Project
            </button>
          </div>

          <div className="space-y-4">
            {profile.projects?.map((proj, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-surface-card border border-border space-y-3 relative group"
              >
                <div className="flex items-center justify-between">
                  <input
                    type="text"
                    value={proj.title}
                    onChange={(e) => {
                      const updated = [...profile.projects];
                      updated[idx].title = e.target.value;
                      setProfile({ ...profile, projects: updated });
                    }}
                    className="font-semibold text-white text-sm bg-transparent border-b border-transparent focus:border-primary focus:outline-none w-3/4"
                    placeholder="Project Title"
                  />
                  <button
                    type="button"
                    onClick={() => removeProject(idx)}
                    className="text-muted hover:text-destructive p-1 transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <textarea
                  rows={2}
                  value={proj.description}
                  onChange={(e) => {
                    const updated = [...profile.projects];
                    updated[idx].description = e.target.value;
                    setProfile({ ...profile, projects: updated });
                  }}
                  className="w-full p-2.5 rounded-lg bg-surface border border-border/60 text-xs text-slate-300 focus:outline-none focus:border-primary"
                  placeholder="Describe what you engineered, algorithms or systems built..."
                />

                <input
                  type="text"
                  value={proj.technologies?.join(", ") || ""}
                  onChange={(e) => {
                    const updated = [...profile.projects];
                    updated[idx].technologies = e.target.value.split(",").map((s) => s.trim()).filter(Boolean);
                    setProfile({ ...profile, projects: updated });
                  }}
                  className="w-full px-2.5 py-1.5 rounded-lg bg-surface border border-border/60 text-xs text-slate-300 focus:outline-none focus:border-primary font-mono"
                  placeholder="Technologies (e.g. Python, FastAPI, Docker)"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Save Bar */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-primary hover:bg-primary-hover text-white text-sm font-medium shadow-glow transition-all"
          >
            <Save className="w-4 h-4" />
            {saving ? "Saving Changes..." : "Save Profile"}
          </button>
        </div>
      </form>
    </div>
  );
}
