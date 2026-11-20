"use client";

import React, { useState } from "react";
import Navbar from "../components/Navbar";
import { Sparkles, Sliders, CheckCircle2 } from "lucide-react";
import { useRouter } from "next/navigation";

export default function StudioPage() {
  const router = useRouter();
  const [genTopic, setGenTopic] = useState("");
  const [genNiche, setGenNiche] = useState("Almost Real (Hyperrealistic Scenarios)");
  const [genVoice, setGenVoice] = useState("en-US-ChristopherNeural");
  const [genAutoPublish, setGenAutoPublish] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generationMsg, setGenerationMsg] = useState("");
  const [scriptPreview, setScriptPreview] = useState<any>(null);
  const [previewing, setPreviewing] = useState(false);

  const handleGenerate = async () => {
    setGenerating(true);
    setGenerationMsg("Sending request to Almost Real AI video pipeline...");
    try {
      const res = await fetch("/api/v1/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: genTopic || null,
          niche: genNiche,
          voice: genVoice,
          auto_publish_facebook: genAutoPublish
        })
      });
      const data = await res.json();
      setGenerationMsg(data.message || "Video generation started!");
      setTimeout(() => {
        router.push("/");
      }, 1500);
    } catch (e: any) {
      setGenerationMsg(`Error: ${e.message}`);
      setGenerating(false);
    }
  };

  const handlePreviewScript = async () => {
    setPreviewing(true);
    setScriptPreview(null);
    try {
      const res = await fetch("/api/v1/generate/preview-script", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: genTopic || null,
          niche: genNiche,
          voice: genVoice
        })
      });
      if (res.ok) {
        const data = await res.json();
        setScriptPreview(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setPreviewing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-8 flex-1 w-full">
        <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Autonomous Reel Studio</h2>
              <p className="text-xs text-slate-400">Configure topic &amp; voice, or let Gemini brainstorm hyperrealistic viral concepts</p>
            </div>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-2">
                Concept / Topic (Optional)
              </label>
              <input
                type="text"
                value={genTopic}
                onChange={(e) => setGenTopic(e.target.value)}
                placeholder="e.g. What If Gravity Inverted For 10 Seconds?, or leave blank for auto-curation"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
              />
              <p className="text-xs text-slate-500 mt-1.5">
                Leave blank to let Gemini curate high-retention scenarios for your selected niche.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-2">
                  Target Niche
                </label>
                <select
                  value={genNiche}
                  onChange={(e) => setGenNiche(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="Almost Real (Hyperrealistic Scenarios)">Almost Real (Hyperrealistic Scenarios)</option>
                  <option value="Tech & AI Horizons">Tech & AI Horizons</option>
                  <option value="Mindset & Stoic Wisdom">Mindset & Stoic Wisdom</option>
                  <option value="Curious Realities & Facts">Curious Realities & Facts</option>
                  <option value="Daily Wealth & Success">Daily Wealth & Success</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-2">
                  Neural Voice (Edge-TTS)
                </label>
                <select
                  value={genVoice}
                  onChange={(e) => setGenVoice(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="en-US-ChristopherNeural">Christopher (Deep, Authoritative Male)</option>
                  <option value="en-US-GuyNeural">Guy (Energetic, Dynamic Male)</option>
                  <option value="en-US-JennyNeural">Jenny (Warm, Expressive Female)</option>
                  <option value="en-US-AriaNeural">Aria (Clear, Professional Female)</option>
                  <option value="en-GB-RyanNeural">Ryan (Sophisticated British Male)</option>
                </select>
              </div>
            </div>

            <div className="flex items-center gap-3 bg-slate-950/60 border border-slate-800/80 p-4 rounded-xl">
              <input
                type="checkbox"
                id="autoPub"
                checked={genAutoPublish}
                onChange={(e) => setGenAutoPublish(e.target.checked)}
                className="w-4 h-4 text-indigo-600 rounded bg-slate-900 border-slate-700"
              />
              <label htmlFor="autoPub" className="text-sm text-slate-300 cursor-pointer">
                <span className="font-semibold text-white">Auto-Publish to Facebook immediately</span>
                <span className="block text-xs text-slate-500">
                  When rendered, upload directly to your connected Facebook Page.
                </span>
              </label>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold py-3.5 px-6 rounded-xl text-sm shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Sparkles className={`w-4 h-4 ${generating ? "animate-spin" : ""}`} />
                <span>{generating ? "Generating Reel..." : "Generate Reel Now"}</span>
              </button>

              <button
                onClick={handlePreviewScript}
                disabled={previewing}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold py-3.5 px-6 rounded-xl text-sm border border-slate-700 flex items-center justify-center gap-2"
              >
                <Sliders className={`w-4 h-4 ${previewing ? "animate-spin" : ""}`} />
                <span>Preview Script</span>
              </button>
            </div>

            {generationMsg && (
              <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-sm">
                {generationMsg}
              </div>
            )}
          </div>

          {scriptPreview && (
            <div className="mt-8 pt-8 border-t border-slate-800">
              <h3 className="font-bold text-lg text-white mb-3">Script Preview</h3>
              <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-4">
                <div>
                  <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Title</span>
                  <p className="text-base font-bold text-white mt-0.5">{scriptPreview.title}</p>
                </div>

                <div>
                  <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Spoken Hook</span>
                  <p className="text-sm italic text-slate-200 mt-0.5 bg-amber-500/10 p-3 rounded-lg border border-amber-500/20">
                    "{scriptPreview.hook}"
                  </p>
                </div>

                <div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Scenes</span>
                  <div className="space-y-2 mt-2">
                    {scriptPreview.scenes?.map((sc: any, i: number) => (
                      <div key={i} className="p-3 bg-slate-900 rounded-xl text-xs space-y-1">
                        <div className="font-semibold text-indigo-300">Scene {sc.scene_number || i + 1}</div>
                        <p className="text-slate-300"><span className="text-slate-500">Narration:</span> {sc.narration}</p>
                        <p className="text-slate-400"><span className="text-slate-500">Visual Prompt:</span> {sc.visual_prompt}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Caption &amp; Hashtags</span>
                  <p className="text-xs text-slate-300 whitespace-pre-line mt-1 bg-slate-900 p-3 rounded-xl">
                    {scriptPreview.caption}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
