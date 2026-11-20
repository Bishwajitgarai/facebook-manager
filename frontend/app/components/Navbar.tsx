"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Film, Sparkles, Calendar, Share2, Tv } from "lucide-react";

export default function Navbar({ videoCount = 0 }: { videoCount?: number }) {
  const pathname = usePathname();

  const navItems = [
    { href: "/", label: "Video Library", icon: Tv, badge: videoCount > 0 ? videoCount : undefined },
    { href: "/studio", label: "Reel Studio", icon: Sparkles },
    { href: "/scheduler", label: "Daily Autopilot", icon: Calendar },
    { href: "/social", label: "Social Sync", icon: Share2 },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <Film className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-300 bg-clip-text text-transparent">
                Almost Real AI
              </span>
              <span className="text-[10px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-medium">
                Studio
              </span>
            </div>
            <p className="text-xs text-slate-400">Gemini Video Engine &amp; Social Sync</p>
          </div>
        </Link>

        <div className="flex items-center gap-2">
          <Link
            href="/studio"
            className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white px-4 py-2 rounded-xl text-sm font-semibold shadow-lg shadow-indigo-600/30 transition-all hover:scale-[1.02]"
          >
            <Sparkles className="w-4 h-4" />
            <span>Create Reel</span>
          </Link>
        </div>
      </div>

      {/* Dynamic Nav Items */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex gap-2 overflow-x-auto pb-2 scrollbar-none">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-indigo-400" : ""}`} />
              <span>{item.label}</span>
              {item.badge !== undefined && (
                <span className="text-xs bg-slate-800 px-1.5 py-0.5 rounded-full text-slate-300">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </div>
    </header>
  );
}
