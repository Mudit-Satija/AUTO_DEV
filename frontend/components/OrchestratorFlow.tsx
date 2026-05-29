"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Clock, Zap } from "lucide-react";

interface OrchestratorFlowProps {
  phase: string;
  validationData: any;
}

export default function OrchestratorFlow({
  phase,
  validationData,
}: OrchestratorFlowProps) {
  const steps = [
    { id: "chat", label: "User Input", icon: "💬", description: "Interactive dialogue" },
    { id: "validation", label: "Validation", icon: "✓", description: "Analyze requirements" },
    { id: "planning", label: "Planning", icon: "🏗️", description: "Generate architecture" },
    { id: "result", label: "Result", icon: "✨", description: "Final architecture" },
  ];

  const getStepStatus = (stepId: string) => {
    if (stepId === "chat") return "completed";
    if (stepId === "validation" && phase !== "chat") return "completed";
    if (stepId === "planning" && phase === "result") return "completed";
    if (stepId === "result" && phase === "result") return "completed";
    if (stepId === "planning" && phase === "planning") return "active";
    if (stepId === "validation" && phase !== "chat") return "active";
    return "pending";
  };

  return (
    <div className="glass p-6 space-y-8">
      {/* Workflow Steps */}
      <div>
        <h3 className="text-sm font-semibold text-slate-300 mb-6 uppercase tracking-wider">
          Orchestration Flow
        </h3>

        <div className="space-y-4">
          {steps.map((step, index) => {
            const status = getStepStatus(step.id);
            const isLast = index === steps.length - 1;

            return (
              <div key={step.id}>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-4"
                >
                  {/* Step Indicator */}
                  <div className="flex flex-col items-center flex-shrink-0">
                    <motion.div
                      animate={
                        status === "active"
                          ? { scale: [1, 1.1, 1] }
                          : status === "completed"
                          ? { scale: 1 }
                          : { scale: 1 }
                      }
                      transition={
                        status === "active"
                          ? { repeat: Infinity, duration: 1 }
                          : { duration: 0 }
                      }
                      className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-base transition-all ${
                        status === "completed"
                          ? "bg-green-900/50 border border-green-500/50 text-green-300"
                          : status === "active"
                          ? "bg-blue-900/50 border border-blue-500/50 text-blue-300 pulse-glow"
                          : "bg-slate-800/50 border border-slate-700/50 text-slate-500"
                      }`}
                    >
                      {status === "completed" ? (
                        <CheckCircle2 size={20} />
                      ) : status === "active" ? (
                        <Zap size={20} />
                      ) : (
                        <Clock size={20} />
                      )}
                    </motion.div>

                    {/* Connecting Line */}
                    {!isLast && (
                      <motion.div
                        initial={{ scaleY: 0 }}
                        animate={{ scaleY: 1 }}
                        transition={{ delay: index * 0.1 + 0.2, duration: 0.4 }}
                        className={`w-0.5 h-12 mt-1 transition-colors ${
                          status === "completed" ||
                          (getStepStatus(steps[index + 1].id) !== "pending" &&
                            status !== "pending")
                            ? "bg-green-500/30"
                            : "bg-slate-700/30"
                        }`}
                      />
                    )}
                  </div>

                  {/* Step Content */}
                  <div className="pt-1 flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">{step.icon}</span>
                      <h4 className="font-semibold text-slate-100">{step.label}</h4>
                    </div>
                    <p className="text-xs text-slate-400">{step.description}</p>

                    {/* Step Details */}
                    {status !== "pending" && step.id === "validation" && validationData && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        className="mt-3 bg-slate-900/30 border border-slate-700/30 rounded p-3 space-y-1 text-xs"
                      >
                        <div>
                          <span className="text-slate-400">Type:</span>
                          <span className="text-blue-300 font-medium ml-2">
                            {validationData.project_type}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-400">Complexity:</span>
                          <span className="text-cyan-300 font-medium ml-2">
                            {validationData.complexity}
                          </span>
                        </div>
                      </motion.div>
                    )}
                  </div>
                </motion.div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Stats */}
      {validationData && (
        <div className="border-t border-slate-700/30 pt-6">
          <h4 className="text-sm font-semibold text-slate-300 mb-3">Analysis Summary</h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-900/30 border border-slate-700/30 rounded p-3">
              <p className="text-xs text-slate-400">Project Type</p>
              <p className="font-semibold text-blue-300">
                {validationData.project_type || "Unknown"}
              </p>
            </div>
            <div className="bg-slate-900/30 border border-slate-700/30 rounded p-3">
              <p className="text-xs text-slate-400">Complexity</p>
              <p className="font-semibold text-cyan-300">
                {validationData.complexity || "Unknown"}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
