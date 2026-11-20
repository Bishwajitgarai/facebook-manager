"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import Navbar from "./components/Navbar";
import {
  Play,
  Film,
  Sparkles,
  Share2,
  Calendar,
  HardDrive,
  CheckCircle2,
  Clock,
  Trash2,
  RefreshCw,
  Download,
  ExternalLink
} from "lucide-react";

const FacebookIcon = ({ className = "w-4 h-4", size = 16 }: { className?: string; size?: number }) => (
  <svg
    className={className}
    style={{ width: `${size}px`, height: `${size}px`, minWidth: `${size}px`, minHeight: `${size}px`, display: "inline-block" }}
    viewBox="0 0 24 24"
    fill="currentColor"
  >
    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
  </svg>
);

const API_BASE = "";

interface VideoItem {
  id: number;
  uuid: string;
  title: string;
  topic: string;
  niche: string;
  hook?: string;
  narration_text?: string;
  caption?: string;
  status: string;
  video_path?: string;
  thumbnail_path?: string;
  duration_seconds: number;
  file_size_bytes: number;
  resolution: string;
  created_at: string;
  posts: Array<{
    id: number;
    platform: string;
    status: string;
    platform_post_id?: string;
    platform_url?: string;
  }>;
}

interface StatsData {
  total_videos: number;
  ready_videos: number;
  posted_videos: number;
  total_storage_mb: number;
  next_scheduled_run?: string;
  last_run_status?: string;
  facebook_connected: boolean;
  gemini_connected: boolean;
  default_niche: string;
}

export default function LibraryPage() {
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState<VideoItem | null>(null);

  const fetchData = async () => {
    try {
      setRefreshing(true);
      const [vRes, sRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/videos`),
        fetch(`${API_BASE}/api/v1/stats`)
      ]);
      if (vRes.ok) {
        const vData = await vRes.json();
        setVideos(vData);
      }
      if (sRes.ok) {
        const sData = await sRes.json();
        setStats(sData);
      }
    } catch (e) {
      console.error("Failed to fetch dashboard data:", e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 8000);
    return () => clearInterval(interval);
  }, []);

  const handlePublishFacebook = async (video: VideoItem) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/publish/${video.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          platforms: ["FACEBOOK"],
          custom_caption: video.caption
        })
      });
      const data = await res.json();
      if (data.results?.FACEBOOK?.success) {
        alert("Video successfully published to Facebook Page!");
      } else {
        alert(`Facebook publish note: ${data.results?.FACEBOOK?.error || "Error uploading"}`);
      }
      fetchData();
    } catch (e: any) {
      alert(`Publish error: ${e.message}`);
    }
  };

  const handleDeleteVideo = async (id: number) => {
    if (!confirm("Delete this video from database and local storage?")) return;
    try {
      await fetch(`${API_BASE}/api/v1/videos/${id}`, { method: "DELETE" });
      fetchData();
      if (selectedVideo?.id === id) setSelectedVideo(null);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar videoCount={videos.length} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-2xl flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Stored Videos</p>
              <h3 className="text-2xl font-bold mt-1 text-white">{stats?.total_videos ?? videos.length}</h3>
              <p className="text-xs text-emerald-400 flex items-center gap-1 mt-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> PostgreSQL Synced
              </p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center">
              <Film className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-2xl flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Published to Facebook</p>
              <h3 className="text-2xl font-bold mt-1 text-white">{stats?.posted_videos ?? 0}</h3>
              <p className="text-xs text-indigo-400 flex items-center gap-1 mt-1">
                <Share2 className="w-3.5 h-3.5" /> Active Posts
              </p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
              <FacebookIcon className="w-6 h-6" size={24} />
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-2xl flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Local Disk Storage</p>
              <h3 className="text-2xl font-bold mt-1 text-white">{stats?.total_storage_mb ?? 0} MB</h3>
              <p className="text-xs text-slate-400 flex items-center gap-1 mt-1">
                <HardDrive className="w-3.5 h-3.5" /> Persistent Volume
              </p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <HardDrive className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-2xl flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Daily Auto-Schedule</p>
              <h3 className="text-base font-bold mt-1 text-indigo-300">
                {stats?.next_scheduled_run ? "Active at 10:00 AM" : "Active"}
              </h3>
              <p className="text-xs text-slate-400 flex items-center gap-1 mt-1">
                <Clock className="w-3.5 h-3.5" /> Autonomous Daily Push
              </p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center">
              <Calendar className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Video Library Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-white">Local Video Archive</h2>
            <p className="text-sm text-slate-400">All generated 9:16 vertical reels saved on your storage volume</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchData}
              disabled={refreshing}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
              title="Refresh"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin text-indigo-400" : ""}`} />
            </button>
            <span className="text-xs bg-slate-800/80 text-slate-400 px-3 py-1.5 rounded-lg border border-slate-700/60">
              Format: 1080x1920 MP4
            </span>
          </div>
        </div>

        {/* Videos Grid */}
        {loading ? (
          <div className="p-12 text-center text-slate-400">Loading library...</div>
        ) : videos.length === 0 ? (
          <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-12 text-center">
            <Film className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-200">No Videos Generated Yet</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-6">
              Create your first autonomous vertical reel using Gemini and Edge-TTS!
            </p>
            <Link
              href="/studio"
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-xl text-sm font-semibold inline-flex items-center gap-2 shadow-lg shadow-indigo-600/30"
            >
              <Sparkles className="w-4 h-4" /> Generate First Video
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {videos.map((vid) => {
              const fbPost = vid.posts?.find((p) => p.platform === "FACEBOOK");
              return (
                <div
                  key={vid.id}
                  className="bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition-all flex flex-col group"
                >
                  {/* Thumbnail / Video Preview */}
                  <div className="relative aspect-[9/16] max-h-72 w-full bg-slate-950 overflow-hidden flex items-center justify-center">
                    {vid.thumbnail_path ? (
                      <img
                        src={`/api/v1/videos/${vid.id}/thumbnail`}
                        alt={vid.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                    ) : (
                      <div className="text-slate-600 text-sm flex flex-col items-center gap-2">
                        <Film className="w-8 h-8 animate-pulse text-indigo-500" />
                        <span>{vid.status === "GENERATING" ? "Rendering Video..." : "Processing"}</span>
                      </div>
                    )}

                    {/* Status Overlay */}
                    <div className="absolute top-3 left-3">
                      <span
                        className={`text-xs px-2.5 py-1 rounded-full font-semibold shadow-md ${
                          vid.status === "POSTED"
                            ? "bg-emerald-600/90 text-white"
                            : vid.status === "READY"
                            ? "bg-blue-600/90 text-white"
                            : vid.status === "GENERATING"
                            ? "bg-amber-600/90 text-white animate-pulse"
                            : "bg-red-600/90 text-white"
                        }`}
                      >
                        {vid.status}
                      </span>
                    </div>

                    {/* Duration */}
                    {vid.duration_seconds > 0 && (
                      <div className="absolute bottom-3 right-3 bg-black/80 text-white text-xs px-2 py-0.5 rounded-md font-mono">
                        {Math.round(vid.duration_seconds)}s
                      </div>
                    )}

                    {/* Play Button Overlay */}
                    {(vid.status === "READY" || vid.status === "POSTED") && (
                      <button
                        onClick={() => setSelectedVideo(vid)}
                        className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer"
                      >
                        <div className="w-14 h-14 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-xl hover:scale-110 transition-transform">
                          <Play className="w-6 h-6 fill-current ml-1" />
                        </div>
                      </button>
                    )}
                  </div>

                  {/* Body */}
                  <div className="p-5 flex-1 flex flex-col justify-between">
                    <div>
                      <div className="text-xs text-indigo-400 font-medium mb-1">{vid.niche}</div>
                      <Link href={`/videos/${vid.id}`} className="hover:text-indigo-300 transition-colors">
                        <h4 className="font-bold text-base text-slate-100 line-clamp-2 leading-snug">
                          {vid.title}
                        </h4>
                      </Link>
                      {vid.hook && (
                        <p className="text-xs text-slate-400 mt-2 line-clamp-2 italic">
                          "{vid.hook}"
                        </p>
                      )}
                    </div>

                    {/* Footer Actions */}
                    <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between gap-2">
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => setSelectedVideo(vid)}
                          className="px-3 py-1.5 rounded-lg bg-indigo-600/20 text-indigo-300 hover:bg-indigo-600/30 text-xs font-semibold flex items-center gap-1.5"
                        >
                          <Play className="w-3.5 h-3.5 fill-current" /> Watch
                        </button>

                        <button
                          onClick={() => handlePublishFacebook(vid)}
                          title="Publish to Facebook Page"
                          className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 ${
                            fbPost?.status === "SUCCESS"
                              ? "bg-emerald-600/20 text-emerald-300 border border-emerald-500/30"
                              : "bg-blue-600 text-white hover:bg-blue-500"
                          }`}
                        >
                          <FacebookIcon className="w-3.5 h-3.5" />
                          {fbPost?.status === "SUCCESS" ? "Published" : "Post to FB"}
                        </button>
                      </div>

                      <div className="flex items-center gap-1">
                        <Link
                          href={`/videos/${vid.id}`}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-slate-800"
                          title="View Dynamic Route"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={() => handleDeleteVideo(vid.id)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      {/* Modal Video Player */}
      {selectedVideo && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden max-w-sm w-full shadow-2xl flex flex-col max-h-[92vh]">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h4 className="font-bold text-sm text-white line-clamp-1">{selectedVideo.title}</h4>
                <p className="text-xs text-slate-400">{selectedVideo.niche}</p>
              </div>
              <button
                onClick={() => setSelectedVideo(null)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            <div className="relative aspect-[9/16] bg-black flex items-center justify-center overflow-hidden">
              <video
                src={`/api/v1/videos/${selectedVideo.id}/stream`}
                controls
                autoPlay
                className="w-full h-full object-contain"
              />
            </div>

            <div className="p-4 bg-slate-950 border-t border-slate-800 flex items-center justify-between gap-2">
              <a
                href={`/api/v1/videos/${selectedVideo.id}/stream`}
                download={`${selectedVideo.uuid}.mp4`}
                className="flex items-center gap-1.5 text-xs text-slate-300 hover:text-white bg-slate-800 px-3 py-2 rounded-xl"
              >
                <Download className="w-3.5 h-3.5" /> Save MP4
              </a>

              <button
                onClick={() => handlePublishFacebook(selectedVideo)}
                className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5"
              >
                <FacebookIcon className="w-3.5 h-3.5" /> Post to FB
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
