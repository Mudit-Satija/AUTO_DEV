"use client";

import { useEffect, useState } from "react";
import OrchestratorFlow from "@/components/OrchestratorFlow";
import InteractiveChat from "@/components/InteractiveChat";
import ArchitectureResult from "@/components/ArchitectureResult";
import FrontendArchitecture from "@/components/FrontendArchitecture";
import { motion } from "framer-motion";

export default function Home() {
  const [phase, setPhase] = useState<"chat" | "planning" | "result">("chat");
  const [validationData, setValidationData] = useState<any>(null);
  const [architectureData, setArchitectureData] = useState<any>(null);
  const [modelInfo, setModelInfo] = useState<any>(null);
  const [generating, setGenerating] = useState(false);
  const [generationResult, setGenerationResult] = useState<any>(null);
  const [logs, setLogs] = useState<Array<{ id: string; type: string; text: string; time: string }>>([]);

  // Fetch model info on mount
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

  const addLog = (type: string, text: string) => {
    const time = new Date().toLocaleTimeString("en-US", { hour12: false });
    setLogs((prev) => [...prev, { id: Math.random().toString(), type, text, time }]);
  };

  const handleValidationComplete = (data: any) => {
    setValidationData(data);
    addLog("success", `✓ Validation complete: ${data.project_type}`);
    setPhase("planning");
  };

  const handleArchitecturePlanningComplete = (architecturePlan: any) => {
    setArchitectureData(architecturePlan);
    addLog("success", "✓ Backend and frontend architecture plans generated");
    setPhase("result");
  };

  const handleReset = () => {
    setPhase("chat");
    setValidationData(null);
    setArchitectureData(null);
    setGenerationResult(null);
    setLogs([]);
  };

  const handleGenerateProject = async () => {
    if (!architectureData?.build_plan || !architectureData?.project_rules) return;
    setGenerating(true);
    setGenerationResult(null);
    addLog("info", "→ Generating project files...");
    try {
      const response = await fetch("http://localhost:8000/generate-project", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          build_plan: architectureData.build_plan,
          project_rules: architectureData.project_rules,
        }),
      });
      if (!response.ok) throw new Error("API error");
      const data = await response.json();
      setGenerationResult(data);
      addLog("success", `✓ Project generated: ${data.files_generated} files written`);
    } catch (error) {
      addLog("error", `✗ Project generation failed: ${error}`);
    } finally {
      setGenerating(false);
    }
  };

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
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Chat/Input Column */}
          <div className="lg:col-span-1 order-2 lg:order-1 min-h-0">
            <InteractiveChat 
              onValidationComplete={handleValidationComplete}
              addLog={addLog}
              phase={phase}
              onPlanArchitecture={async (validationPayload) => {
                addLog("info", "→ Starting backend + frontend planning in parallel...");
                try {
                  const response = await fetch("http://localhost:8000/plan-full-architecture", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ validation_output: validationPayload }),
                  });
                  if (!response.ok) throw new Error("API error");
                  const data = await response.json();
                  if (data.status !== "success") {
                    throw new Error(data.reasoning || "Planning failed");
                  }
                  handleArchitecturePlanningComplete(data);
                } catch (error) {
                  addLog("error", `✗ Full architecture planning failed: ${error}`);
                }
              }}
            />
          </div>

          {/* Orchestrator & Results Column */}
          <div className="lg:col-span-3 order-1 lg:order-2 space-y-6">
            <OrchestratorFlow 
              phase={phase}
              validationData={validationData}
            />

            {phase === "result" && architectureData && (
              <div className="space-y-6">
                <ArchitectureResult
                  data={architectureData.backend_architecture}
                  onNewProject={handleReset}
                />
                <FrontendArchitecture data={architectureData} />

                {architectureData.project_rules && (
                  <details className="glass rounded-lg group">
                    <summary className="px-6 py-4 cursor-pointer text-sm font-semibold text-slate-300 hover:text-slate-100 transition-colors flex items-center justify-between list-none [&::-webkit-details-marker]:hidden">
                      <span>Project Rules</span>
                      <span className="text-slate-500 group-open:rotate-180 transition-transform">▼</span>
                    </summary>
                    <div className="px-6 pb-4 border-t border-slate-700/30 pt-3">
                      <pre className="text-xs text-slate-400 font-mono whitespace-pre-wrap break-words">
                        {JSON.stringify(architectureData.project_rules, null, 2)}
                      </pre>
                    </div>
                  </details>
                )}

                {architectureData.build_plan && (
                  <details className="glass rounded-lg group">
                    <summary className="px-6 py-4 cursor-pointer text-sm font-semibold text-slate-300 hover:text-slate-100 transition-colors flex items-center justify-between list-none [&::-webkit-details-marker]:hidden">
                      <span>Build Plan</span>
                      <span className="text-slate-500 group-open:rotate-180 transition-transform">▼</span>
                    </summary>
                    <div className="px-6 pb-4 border-t border-slate-700/30 pt-3">
                      <div className="space-y-2">
                        {(architectureData.build_plan.files ?? []).map((file: any, idx: number) => (
                          <div key={idx} className="flex items-start gap-3 p-2 bg-slate-900/30 border border-slate-700/30 rounded text-xs">
                            <span className="text-blue-400 font-mono flex-shrink-0">{file.path}</span>
                            <span className="text-slate-500">—</span>
                            <span className="text-slate-400">{file.purpose}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </details>
                )}

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleGenerateProject}
                  disabled={generating}
                  className="w-full btn-primary flex items-center justify-center gap-2 py-3"
                >
                  {generating ? (
                    <>Generating...</>
                  ) : (
                    <>Generate Project</>
                  )}
                </motion.button>

                {generationResult && (
                  <div className="glass p-4 text-sm text-green-400">
                    Generated {generationResult.files_generated} files
                    {generationResult.registry_path && (
                      <span className="block text-xs text-slate-400 mt-1">
                        Registry: {generationResult.registry_path}
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Logs Panel - Bottom */}
      <div className="border-t border-slate-800/50 bg-slate-950/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="glass-dark p-4 max-h-40 overflow-y-auto">
            <div className="text-xs font-mono space-y-1">
              {logs.map((log) => (
                <div key={log.id} className={`flex gap-2 ${
                  log.type === "success" ? "text-green-400" :
                  log.type === "error" ? "text-red-400" :
                  log.type === "warning" ? "text-yellow-400" :
                  "text-blue-400"
                }`}>
                  <span className="text-slate-500 w-8 flex-shrink-0">[{log.time}]</span>
                  <span className="flex-shrink-0">{log.type.toUpperCase()}</span>
                  <span className="text-slate-300">{log.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
