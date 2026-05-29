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
  const [frontendData, setFrontendData] = useState<any>(null);
  const [modelInfo, setModelInfo] = useState<any>(null);
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

  const handleFrontendPlanningComplete = (frontendPlan: any) => {
    setFrontendData(frontendPlan);
    addLog("success", `✓ Frontend architecture plan generated`);
    setPhase("result");
  };

  const handleReset = () => {
    setPhase("chat");
    setValidationData(null);
    setFrontendData(null);
    setLogs([]);
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
          <div className="lg:col-span-1 order-2 lg:order-1">
            <InteractiveChat 
              onValidationComplete={handleValidationComplete}
              addLog={addLog}
              phase={phase}
              onPlanFrontend={async (validationPayload) => {
                addLog("info", "→ Starting frontend planning...");
                try {
                  const response = await fetch("http://localhost:8000/plan-frontend", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ validation_output: validationPayload }),
                  });
                  if (!response.ok) throw new Error("API error");
                  const data = await response.json();
                  handleFrontendPlanningComplete(data);
                } catch (error) {
                  addLog("error", `✗ Frontend planning failed: ${error}`);
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

            {phase === "result" && frontendData && (
              <FrontendArchitecture data={frontendData} />
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
