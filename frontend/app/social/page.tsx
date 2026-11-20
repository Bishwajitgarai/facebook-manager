"use client";

import React, { useState } from "react";
import Navbar from "../components/Navbar";
import { Share2, RefreshCw, CheckCircle2, AlertCircle } from "lucide-react";

const FacebookIcon = ({ className = "w-6 h-6" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
  </svg>
);

const InstagramIcon = ({ className = "w-6 h-6" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
  </svg>
);

const YoutubeIcon = ({ className = "w-6 h-6" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
  </svg>
);

export default function SocialPage() {
  const [fbStatus, setFbStatus] = useState<any>(null);
  const [testingFb, setTestingFb] = useState(false);

  const handleTestFacebook = async () => {
    setTestingFb(true);
    try {
      const res = await fetch("/api/v1/publish/facebook/status");
      const data = await res.json();
      setFbStatus(data);
    } catch (e: any) {
      setFbStatus({ connected: false, message: e.message });
    } finally {
      setTestingFb(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8 flex-1 w-full">
        <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-white">Social Platform Connections</h2>
              <p className="text-xs text-slate-400">Configure Facebook Page and inspect Instagram / YouTube adapters</p>
            </div>
            <button
              onClick={handleTestFacebook}
              disabled={testingFb}
              className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${testingFb ? "animate-spin" : ""}`} />
              Test Facebook Connection
            </button>
          </div>

          {fbStatus && (
            <div
              className={`p-4 rounded-2xl mb-6 border text-sm ${
                fbStatus.connected
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                  : "bg-red-500/10 border-red-500/30 text-red-300"
              }`}
            >
              <p className="font-semibold">{fbStatus.message}</p>
              {fbStatus.connected && (
                <div className="mt-2 text-xs text-slate-300 space-y-1">
                  <p>Page ID: {fbStatus.page_id}</p>
                  <p>Followers: {fbStatus.followers}</p>
                </div>
              )}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-xl bg-blue-600/20 text-blue-400 flex items-center justify-center mb-4">
                  <FacebookIcon className="w-6 h-6" />
                </div>
                <h3 className="font-bold text-white text-base">Facebook Pages</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Auto-upload vertical Reels and standard video posts via Graph API v21.0
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-800">
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  Active Adapter
                </span>
              </div>
            </div>

            <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-xl bg-pink-600/20 text-pink-400 flex items-center justify-center mb-4">
                  <InstagramIcon className="w-6 h-6" />
                </div>
                <h3 className="font-bold text-white text-base">Instagram Reels</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Instagram Graph API Container adapter prepared in backend/services/social/instagram.py
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-800">
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-800 text-slate-400">
                  Ready for Token
                </span>
              </div>
            </div>

            <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-xl bg-red-600/20 text-red-400 flex items-center justify-center mb-4">
                  <YoutubeIcon className="w-6 h-6" />
                </div>
                <h3 className="font-bold text-white text-base">YouTube Shorts</h3>
                <p className="text-xs text-slate-400 mt-1">
                  YouTube Data API v3 upload adapter prepared in backend/services/social/youtube.py
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-800">
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-800 text-slate-400">
                  Ready for Token
                </span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
