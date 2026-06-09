"use client";

import { useEffect, useState } from "react";
import InteractiveChat from "@/components/InteractiveChat";
import { motion } from "framer-motion";

export default function Home() {
  const [modelInfo, setModelInfo] = useState<any>(null);

  useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        const response = await fetch("http://localhost:8000/info");
        if (response.ok) {
          const data = await response.json();
          setModelInfo(data);
        }
      } catch (error) {
        console.log("Could not fetch model info");
      }
    };
    fetchModelInfo();
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800/50 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="text-2xl">⚙</div>
              <div>
                <h1 className="text-xl font-bold gradient-text">AUTO.DEV</h1>
                <p className="text-xs text-slate-400">Full-Stack AI Architecture Planning</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {modelInfo && (
                <motion.div
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-xs text-slate-400 text-right"
                >
                  <div>Validation: {modelInfo.validation_model}</div>
                  <div>Planning: {modelInfo.backend_model}</div>
                  <div>Frontend: {modelInfo.frontend_model}</div>
                </motion.div>
              )}
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="w-2 h-2 bg-blue-500 rounded-full pulse-glow"
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
        <InteractiveChat />
      </main>
    </div>
  );
}
