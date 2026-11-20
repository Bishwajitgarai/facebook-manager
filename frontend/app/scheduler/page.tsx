"use client";

import React, { useState } from "react";
import Navbar from "../components/Navbar";
import { Calendar, Clock, CheckCircle2 } from "lucide-react";

export default function SchedulerPage() {
  const [schedHour, setSchedHour] = useState(10);
  const [schedMinute, setSchedMinute] = useState(0);
  const [schedAutoPublish, setSchedAutoPublish] = useState(false);
  const [schedNiche, setSchedNiche] = useState("Almost Real (Hyperrealistic Scenarios)");
  const [schedSavedMsg, setSchedSavedMsg] = useState("");

  const handleSaveSchedule = async () => {
    try {
      const res = await fetch("/api/v1/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          hour: Number(schedHour),
          minute: Number(schedMinute),
          auto_publish: schedAutoPublish,
          niche: schedNiche
        })
      });
      const data = await res.json();
      setSchedSavedMsg(data.message || "Schedule updated successfully!");
      setTimeout(() => setSchedSavedMsg(""), 4000);
    } catch (e: any) {
      setSchedSavedMsg(`Error: ${e.message}`);
    }
  };

  const handleRunDailyNow = async () => {
    try {
      await fetch("/api/v1/schedule/run-now", { method: "POST" });
      alert("Daily automation run triggered! Creating script and compiling video...");
    } catch (e: any) {
      alert(`Failed to trigger: ${e.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-8 flex-1 w-full">
        <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <Calendar className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Daily Autopilot Scheduler</h2>
              <p className="text-xs text-slate-400">APScheduler triggers script generation, rendering, and publishing daily</p>
            </div>
          </div>

          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-2">Schedule Hour (0-23)</label>
                <input
                  type="number"
                  min={0}
                  max={23}
                  value={schedHour}
                  onChange={(e) => setSchedHour(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-2">Schedule Minute (0-59)</label>
                <input
                  type="number"
                  min={0}
                  max={59}
                  value={schedMinute}
                  onChange={(e) => setSchedMinute(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-2">Automated Topic Niche</label>
              <select
                value={schedNiche}
                onChange={(e) => setSchedNiche(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100"
              >
                <option value="Almost Real (Hyperrealistic Scenarios)">Almost Real (Hyperrealistic Scenarios)</option>
                <option value="Tech & AI Horizons">Tech & AI Horizons</option>
                <option value="Mindset & Stoic Wisdom">Mindset & Stoic Wisdom</option>
                <option value="Curious Realities & Facts">Curious Realities & Facts</option>
                <option value="Daily Wealth & Success">Daily Wealth & Success</option>
              </select>
            </div>

            <div className="flex items-center gap-3 bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
              <input
                type="checkbox"
                id="schedAutoPub"
                checked={schedAutoPublish}
                onChange={(e) => setSchedAutoPublish(e.target.checked)}
                className="w-4 h-4 text-purple-600 rounded"
              />
              <label htmlFor="schedAutoPub" className="text-sm text-slate-300 cursor-pointer">
                <span className="font-semibold text-white">Auto-Publish to Facebook on completion</span>
                <span className="block text-xs text-slate-500">
                  If disabled, reels are rendered and saved in PostgreSQL as READY for manual review.
                </span>
              </label>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <button
                onClick={handleSaveSchedule}
                className="flex-1 bg-purple-600 hover:bg-purple-500 text-white font-semibold py-3 px-6 rounded-xl text-sm"
              >
                Save Schedule Settings
              </button>

              <button
                onClick={handleRunDailyNow}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold py-3 px-6 rounded-xl text-sm border border-slate-700"
              >
                Run Daily Pipeline Now
              </button>
            </div>

            {schedSavedMsg && (
              <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-300 text-sm">
                {schedSavedMsg}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
