"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Zap, Layout, Palette, Navigation, Sparkles, Accessibility } from "lucide-react";

interface FrontendArchitectureProps {
  data: any;
}

export default function FrontendArchitecture({ data }: FrontendArchitectureProps) {
  const [expandedSection, setExpandedSection] = useState<string>("architecture");

  if (!data || data.status !== "success") {
    return (
      <div className="text-center py-8">
        <p className="text-red-400">Frontend planning failed</p>
      </div>
    );
  }

  const sections = [
    {
      id: "architecture",
      title: "🏗️ Frontend Architecture",
      icon: Layout,
      content: data.frontend_architecture,
    },
    {
      id: "components",
      title: "🧩 Components",
      icon: Sparkles,
      content: data.components,
    },
    {
      id: "design",
      title: "🎨 Design System",
      icon: Palette,
      content: data.design_system,
    },
    {
      id: "navigation",
      title: "🧭 Navigation",
      icon: Navigation,
      content: data.navigation,
    },
    {
      id: "accessibility",
      title: "♿ Accessibility",
      icon: Accessibility,
      content: data.accessibility,
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Quick Summary */}
        <motion.div
          className="glass-dark p-4 rounded-lg border border-blue-500/30"
          whileHover={{ borderColor: "rgb(59, 130, 246)" }}
        >
          <h3 className="text-sm font-semibold text-blue-400 mb-3 flex items-center gap-2">
            <Zap size={16} /> Frontend Stack
          </h3>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Framework:</span>
              <span className="text-white font-semibold">{data.frontend_architecture?.framework || "N/A"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Language:</span>
              <span className="text-white font-semibold">{data.frontend_architecture?.language || "N/A"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Styling:</span>
              <span className="text-white font-semibold">{data.frontend_architecture?.styling || "N/A"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">WCAG Level:</span>
              <span className="text-green-400 font-semibold">{data.accessibility?.wcag_level || "N/A"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Components:</span>
              <span className="text-white font-semibold">{data.total_components || "N/A"}</span>
            </div>
          </div>
        </motion.div>

        {/* Breakpoints */}
        <motion.div
          className="glass-dark p-4 rounded-lg border border-purple-500/30"
          whileHover={{ borderColor: "rgb(168, 85, 247)" }}
        >
          <h3 className="text-sm font-semibold text-purple-400 mb-3">📱 Responsive Breakpoints</h3>
          <div className="space-y-2 text-xs">
            {data.breakpoints &&
              Object.entries(data.breakpoints).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-slate-400 capitalize">{key}:</span>
                  <span className="text-white font-mono">{String(value)}</span>
                </div>
              ))}
          </div>
        </motion.div>
      </div>

      {/* Detailed Sections */}
      <div className="space-y-3">
        {sections.map((section) => (
          <motion.div
            key={section.id}
            className="glass-dark rounded-lg border border-slate-700/50 overflow-hidden"
            whileHover={{ borderColor: "rgb(148, 163, 184)" }}
          >
            <button
              onClick={() =>
                setExpandedSection(
                  expandedSection === section.id ? "" : section.id
                )
              }
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-800/50 transition-colors"
            >
              <span className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                <section.icon size={16} />
                {section.title}
              </span>
              <motion.div
                animate={{ rotate: expandedSection === section.id ? 180 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <svg
                  className="w-4 h-4 text-slate-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 14l-7 7m0 0l-7-7m7 7V3"
                  />
                </svg>
              </motion.div>
            </button>

            {expandedSection === section.id && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="px-4 py-3 border-t border-slate-700/50 bg-slate-900/20"
              >
                <pre className="text-xs text-slate-300 overflow-x-auto font-mono whitespace-pre-wrap break-words">
                  {JSON.stringify(section.content, null, 2)}
                </pre>
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Reasoning */}
      {data.combined_reasoning && (
        <motion.div
          className="glass-dark p-4 rounded-lg border border-amber-500/30 text-xs text-slate-300 space-y-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <p className="font-semibold text-amber-400 mb-2">💡 Planning Rationale</p>
          <p>{data.combined_reasoning}</p>
        </motion.div>
      )}
    </motion.div>
  );
}
