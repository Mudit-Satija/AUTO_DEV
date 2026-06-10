"use client";

import InteractiveChat from "@/components/InteractiveChat";
import { Sparkles } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Premium Header */}
      <header className="relative border-b border-white/5 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg shadow-blue-500/25">
                <span className="text-lg font-bold text-white">A</span>
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-white/10 to-transparent pointer-events-none" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight">
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-200 via-blue-300 to-cyan-200">
                    AUTO
                  </span>
                  <span className="text-slate-300">.</span>
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-200 to-blue-300">
                    DEV
                  </span>
                </h1>
                <p className="text-[11px] text-slate-500 tracking-wide mt-0.5">
                  Turn ideas into working applications
                </p>
              </div>
            </div>
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.06]">
              <Sparkles size={12} className="text-blue-400" />
              <span className="text-[11px] text-slate-400">AI-Powered Generation</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-[88rem] mx-auto w-full px-4 py-6">
        <InteractiveChat />
      </main>
    </div>
  );
}
