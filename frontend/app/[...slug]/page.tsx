"use client";

import React from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Navbar from "../components/Navbar";
import { ArrowLeft, Compass } from "lucide-react";

export default function DynamicCatchAllPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug;
  const path = Array.isArray(slug) ? slug.join("/") : slug;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="max-w-3xl mx-auto px-4 py-16 flex-1 w-full text-center">
        <div className="w-16 h-16 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center mx-auto mb-6">
          <Compass className="w-8 h-8" />
        </div>

        <h1 className="text-2xl font-bold text-white">Dynamic Route: /{path}</h1>
        <p className="text-sm text-slate-400 mt-2 max-w-md mx-auto">
          This is an active dynamic page route served by Next.js App Router through Nginx.
        </p>

        <div className="mt-8 flex justify-center gap-3">
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs font-semibold hover:bg-slate-800"
          >
            Go Back
          </button>
          <Link
            href="/"
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-xl text-xs font-semibold"
          >
            Video Library
          </Link>
          <Link
            href="/studio"
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-xs font-semibold"
          >
            Reel Studio
          </Link>
        </div>
      </main>
    </div>
  );
}
