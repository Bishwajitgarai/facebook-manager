"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Navbar from "../../components/Navbar";
import { Download, ArrowLeft, Play, Calendar, Film } from "lucide-react";

export default function VideoDetailPage() {
  const params = useParams();
  const router = useRouter();
  const videoId = params?.id;
  const [video, setVideo] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!videoId) return;
    fetch(`/api/v1/videos/${videoId}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        setVideo(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [videoId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
        <Navbar />
        <div className="flex-1 flex items-center justify-center">Loading video #{videoId}...</div>
      </div>
    );
  }

  if (!video) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
        <Navbar />
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
          <Film className="w-12 h-12 text-slate-600 mb-4" />
          <h2 className="text-xl font-bold">Video Not Found</h2>
          <p className="text-slate-400 text-sm mt-1">No video exists with ID #{videoId}</p>
          <Link href="/" className="mt-4 px-4 py-2 bg-indigo-600 rounded-xl text-xs font-semibold">
            Return to Library
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="max-w-4xl mx-auto px-4 py-8 flex-1 w-full">
        <button
          onClick={() => router.push("/")}
          className="inline-flex items-center gap-2 text-xs text-slate-400 hover:text-white mb-6 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Library
        </button>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8">
          {/* 9:16 Video Player */}
          <div className="relative aspect-[9/16] bg-black rounded-2xl overflow-hidden shadow-2xl flex items-center justify-center">
            <video
              src={`/api/v1/videos/${video.id}/stream`}
              controls
              autoPlay
              className="w-full h-full object-contain"
            />
          </div>

          {/* Video Metadata */}
          <div className="flex flex-col justify-between">
            <div className="space-y-4">
              <div>
                <span className="text-xs text-indigo-400 font-semibold uppercase tracking-wider">{video.niche}</span>
                <h1 className="text-2xl font-bold text-white mt-1">{video.title}</h1>
              </div>

              {video.hook && (
                <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-xs italic text-amber-200">
                  "{video.hook}"
                </div>
              )}

              {video.caption && (
                <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-300 whitespace-pre-line">
                  <div className="font-semibold text-slate-400 mb-1 uppercase tracking-wider text-[10px]">Caption</div>
                  {video.caption}
                </div>
              )}

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                  <span className="text-slate-500">Duration</span>
                  <p className="font-bold text-white mt-0.5">{Math.round(video.duration_seconds)}s</p>
                </div>
                <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                  <span className="text-slate-500">Resolution</span>
                  <p className="font-bold text-white mt-0.5">{video.resolution}</p>
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-slate-800 flex gap-3 mt-6">
              <a
                href={`/api/v1/videos/${video.id}/stream`}
                download={`${video.uuid}.mp4`}
                className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 px-4 rounded-xl text-xs flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" /> Download MP4
              </a>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
