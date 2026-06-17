"use client";

import { useState, useMemo, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Download, Loader2, CheckCircle, FileText, RefreshCw, Layout, Database, GitBranch, Circle, Hourglass } from "lucide-react";

type ComplexityOption = "Easy" | "Medium" | "Complex";
type BackendOption = "Express.js" | "FastAPI" | "Frontend Only";
type FrontendOption = "React" | "Vue";

interface ProgressStage {
  id: string;
  label: string;
  duration: number; // ms to stay on this stage
}

const STAGES: ProgressStage[] = [
  { id: "parse", label: "Parsing Requirements", duration: 800 },
  { id: "retrieve", label: "Retrieving Knowledge", duration: 700 },
  { id: "plan", label: "Building Plan", duration: 1200 },
  { id: "generate", label: "Generating Files", duration: 1500 },
  { id: "validate", label: "Running Validation", duration: 900 },
  { id: "package", label: "Packaging ZIP", duration: 600 },
];

type ProgressState = "pending" | "active" | "done";

function parsePages(raw: string): string[] {
  // Pages: simple list of names, comma or newline separated
  return raw
    .split(/[\n,]+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

function parseEntities(raw: string): string[] {
  // Entities: one per line — "EntityName: field1, field2, field3"
  // Split on newlines ONLY; commas separate fields within a definition
  const result: string[] = [];
  for (const line of raw.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    // Parse "Name: field1, field2" into structured tag
    const colonIdx = trimmed.indexOf(":");
    if (colonIdx >= 0) {
      const name = trimmed.slice(0, colonIdx).trim();
      const fields = trimmed
        .slice(colonIdx + 1)
        .split(",")
        .map((f) => f.trim())
        .filter((f) => f.length > 0);
      result.push(`${name}: [${fields.join(", ")}]`);
    } else {
      result.push(trimmed);
    }
  }
  return result;
}

function parseFlow(raw: string): string[] {
  // Flow: one step per line — each line is a full sentence that may contain commas
  return raw
    .split("\n")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

function StageRow({ label, state }: { label: string; state: ProgressState }) {
  const iconMap: Record<ProgressState, React.ReactNode> = {
    pending: <Circle size={14} className="text-slate-600" />,
    active: <Loader2 size={14} className="text-blue-400 animate-spin" />,
    done: <CheckCircle size={14} className="text-emerald-400" />,
  };
  const textMap: Record<ProgressState, string> = {
    pending: "text-slate-600",
    active: "text-slate-200",
    done: "text-slate-300",
  };

  return (
    <div className="flex items-center gap-3 py-1.5">
      <div className="w-5 flex justify-center flex-shrink-0">
        {iconMap[state]}
      </div>
      <span className={`text-xs font-medium transition-colors duration-300 ${textMap[state]}`}>
        {label}
      </span>
    </div>
  );
}

export default function InteractiveChat() {
  const [projectName, setProjectName] = useState("");
  const [complexity, setComplexity] = useState<ComplexityOption>("Medium");
  const [backend, setBackend] = useState<BackendOption>("Frontend Only");
  const [frontend, setFrontend] = useState<FrontendOption>("React");
  const [pagesRaw, setPagesRaw] = useState("");
  const [entitiesRaw, setEntitiesRaw] = useState("");
  const [flowRaw, setFlowRaw] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentStageIndex, setCurrentStageIndex] = useState(-1);
  const [generationResult, setGenerationResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const resultRef = useRef<HTMLDivElement>(null);
  const stageTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const fetchStartRef = useRef<number>(0);

  const parsedPages = useMemo(() => parsePages(pagesRaw), [pagesRaw]);
  const parsedEntities = useMemo(() => parseEntities(entitiesRaw), [entitiesRaw]);
  const parsedFlow = useMemo(() => parseFlow(flowRaw), [flowRaw]);

  const clearStageTimer = useCallback(() => {
    if (stageTimerRef.current) {
      clearTimeout(stageTimerRef.current);
      stageTimerRef.current = null;
    }
  }, []);

  // Advance progress stages while the fetch is in flight
  const startProgress = useCallback(() => {
    setCurrentStageIndex(0);
    fetchStartRef.current = Date.now();

    const advance = (index: number) => {
      if (index >= STAGES.length) return;
      setCurrentStageIndex(index);
      stageTimerRef.current = setTimeout(() => {
        advance(index + 1);
      }, STAGES[index].duration);
    };

    advance(0);
  }, []);

  const stopProgress = useCallback(() => {
    clearStageTimer();
    setCurrentStageIndex(-1);
  }, [clearStageTimer]);

  useEffect(() => {
    return () => clearStageTimer();
  }, [clearStageTimer]);

  useEffect(() => {
    if (generationResult && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [generationResult]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    setError(null);
    setGenerationResult(null);
    startProgress();

    try {
      const isFrontendOnly = backend === "Frontend Only";
      const body = {
        project_name: projectName,
        complexity: complexity.toLowerCase(),
        backend_framework: isFrontendOnly ? "none" : backend,
        frontend_framework: frontend,
        pages: parsedPages,
        entities: parsedEntities,
        flow: parsedFlow,
      };

      const res = await fetch("http://localhost:8000/generate-from-srs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `Generation failed (${res.status})`);
      }

      const data = await res.json();
      setGenerationResult(data);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      stopProgress();
      setIsGenerating(false);
    }
  };

  const renderOption = <T extends string>(
    label: T,
    selected: T,
    onSelect: (v: T) => void,
  ) => (
    <button
      key={label}
      type="button"
      onClick={() => onSelect(label)}
      className={selected === label ? "btn-option-selected" : "btn-option"}
    >
      {label}
    </button>
  );

  // Generic reset
  const resetAll = () => {
    setGenerationResult(null);
    setError(null);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
      {/* ── Left: Configuration Panel ── */}
      <div className="glass-panel flex flex-col overflow-hidden max-h-[780px]">
        <div className="flex-1 overflow-y-auto p-5 pb-0">
          <motion.h2
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-base font-semibold text-slate-100 mb-4"
          >
            Project Configuration
          </motion.h2>

          <form id="config-form" onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Project Name</label>
              <input
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="e.g. StudyHub"
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Complexity</label>
              <div className="flex gap-2">
                {(["Easy", "Medium", "Complex"] as const).map((o) =>
                  renderOption(o, complexity, setComplexity),
                )}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Backend</label>
              <div className="flex gap-2 flex-wrap">
                {(["Express.js", "FastAPI", "Frontend Only"] as const).map((o) =>
                  renderOption(o, backend, setBackend),
                )}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Frontend</label>
              <div className="flex gap-2">
                {(["React", "Vue"] as const).map((o) =>
                  renderOption(o, frontend, setFrontend),
                )}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Pages</label>
              <textarea
                value={pagesRaw}
                onChange={(e) => setPagesRaw(e.target.value)}
                placeholder="One per line or comma separated"
                rows={2}
                className="input-field resize-none"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Entities</label>
              <textarea
                value={entitiesRaw}
                onChange={(e) => setEntitiesRaw(e.target.value)}
                placeholder="One per line or comma separated"
                rows={2}
                className="input-field resize-none"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Flow</label>
              <textarea
                value={flowRaw}
                onChange={(e) => setFlowRaw(e.target.value)}
                placeholder="One per line or comma separated"
                rows={2}
                className="input-field resize-none"
              />
            </div>

            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -4 }}
                  className="text-red-400 text-xs bg-red-900/20 border border-red-800/30 rounded-lg px-3 py-2"
                >
                  {error}
                </motion.div>
              )}
            </AnimatePresence>

            <div className="h-2" />
          </form>
        </div>

        {/* Sticky bottom area: generate button → progress → result */}
        <div className="flex-shrink-0 border-t border-white/[0.06] bg-gradient-to-t from-slate-900/80 to-transparent px-5 py-4 space-y-3">
          <button
            type="submit"
            form="config-form"
            disabled={isGenerating}
            className="btn-generate"
          >
            {isGenerating ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <span className="text-base">🚀</span>
                <span>Generate Project</span>
              </>
            )}
          </button>

          {/* Progress tracker */}
          <AnimatePresence>
            {isGenerating && currentStageIndex >= 0 && !generationResult && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="bg-white/[0.03] border border-white/[0.06] rounded-lg px-4 py-3 overflow-hidden"
              >
                <div className="flex items-center gap-2 mb-2.5">
                  <Hourglass size={12} className="text-blue-400" />
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Generation Progress</span>
                </div>
                {STAGES.map((stage, i) => {
                  let state: ProgressState = "pending";
                  if (i < currentStageIndex) state = "done";
                  else if (i === currentStageIndex) state = "active";
                  return <StageRow key={stage.id} label={stage.label} state={state} />;
                })}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Result card */}
          <AnimatePresence>
            {generationResult && (
              <motion.div
                ref={resultRef}
                initial={{ opacity: 0, y: 12, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 12, scale: 0.98 }}
                transition={{ duration: 0.3 }}
                className="result-card"
              >
                <div className="flex items-center gap-3 pb-3 border-b border-white/[0.06]">
                  <div className="w-10 h-10 rounded-full bg-emerald-500/20 border border-emerald-500/20 flex items-center justify-center flex-shrink-0">
                    <CheckCircle size={20} className="text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-100">Project Generated Successfully</p>
                    <p className="text-xs text-slate-400">{generationResult.files_generated || 0} files generated</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-white/[0.03] rounded-lg px-3 py-2.5 border border-white/[0.04]">
                    <p className="text-xs text-slate-500 mb-0.5">Project Name</p>
                    <p className="text-sm font-medium text-slate-200">{projectName || "Untitled"}</p>
                  </div>
                  <div className="bg-white/[0.03] rounded-lg px-3 py-2.5 border border-white/[0.04]">
                    <p className="text-xs text-slate-500 mb-0.5">Validation</p>
                    <div className="flex items-center gap-1.5">
                      <CheckCircle size={12} className="text-emerald-400" />
                      <span className="text-sm font-medium text-emerald-400">Passed</span>
                    </div>
                  </div>
                </div>

                {generationResult.srs_score !== undefined && (
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs text-slate-400">SRS Quality Score</span>
                      <span className="text-xs font-semibold text-slate-300">{generationResult.srs_score}/100</span>
                    </div>
                    <div className="h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${generationResult.srs_score}%` }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        className={`h-full rounded-full ${
                          generationResult.srs_score >= 71
                            ? "bg-gradient-to-r from-emerald-500 to-emerald-400"
                            : generationResult.srs_score >= 41
                              ? "bg-gradient-to-r from-amber-500 to-amber-400"
                              : "bg-gradient-to-r from-rose-500 to-rose-400"
                        }`}
                      />
                    </div>
                  </div>
                )}

                {generationResult.srs_feedback && (
                  <p className="text-xs text-slate-400 leading-relaxed bg-white/[0.02] rounded-lg px-3 py-2 border border-white/[0.04]">
                    {generationResult.srs_feedback}
                  </p>
                )}

                {generationResult.srs_missing?.length > 0 && (
                  <div>
                    <p className="text-xs text-slate-500 font-medium mb-1.5">Suggestions:</p>
                    <div className="space-y-1">
                      {generationResult.srs_missing.map((item: string, i: number) => (
                        <p key={i} className="text-xs text-slate-400 pl-2 border-l border-amber-500/40">
                          {item}
                        </p>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex gap-3 pt-1">
                  {generationResult?.zip_filename && (
                    <a
                      href={`http://localhost:8000/download/${generationResult.zip_filename}`}
                      download
                      className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-cyan-500 text-white rounded-lg text-sm font-medium transition-all duration-200 shadow-lg shadow-blue-600/20 hover:shadow-blue-500/30 active:scale-[0.98]"
                    >
                      <Download size={16} />
                      Download ZIP
                    </a>
                  )}
                  <button
                    type="button"
                    onClick={resetAll}
                    className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-white/5 border border-white/10 hover:bg-white/10 text-slate-200 rounded-lg text-sm font-medium transition-all duration-200 active:scale-[0.98]"
                  >
                    <RefreshCw size={16} />
                    Generate Again
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* ── Right: SRS Preview ── */}
      <div className="glass-panel-alt p-5 overflow-y-auto max-h-[780px]">
        <div className="flex items-center gap-2.5 mb-5">
          <div className="w-7 h-7 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
            <FileText size={13} className="text-blue-400" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">SRS Preview</h3>
            <p className="text-[10px] text-slate-600 mt-0.5">Software Requirements Specification</p>
          </div>
        </div>

        <div className="space-y-5">
          {projectName || parsedPages.length > 0 || parsedEntities.length > 0 || parsedFlow.length > 0 ? (
            <>
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-white/[0.03] rounded-lg px-3 py-2 border border-white/[0.04]">
                  <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">Project</p>
                  <p className="text-sm font-medium text-slate-200 truncate">{projectName || "Untitled"}</p>
                </div>
                <div className="bg-white/[0.03] rounded-lg px-3 py-2 border border-white/[0.04]">
                  <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">Stack</p>
                  <p className="text-sm font-medium text-slate-200 truncate">{frontend} + {backend === "Frontend Only" ? "None" : backend}</p>
                </div>
                <div className="bg-white/[0.03] rounded-lg px-3 py-2 border border-white/[0.04]">
                  <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">Complexity</p>
                  <p className="text-sm font-medium text-slate-200">{complexity}</p>
                </div>
                <div className="bg-white/[0.03] rounded-lg px-3 py-2 border border-white/[0.04]">
                  <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">Items</p>
                  <p className="text-sm font-medium text-slate-200">{parsedPages.length + parsedEntities.length + parsedFlow.length}</p>
                </div>
              </div>

              <div className="divider-subtle" />

              {parsedPages.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2.5">
                    <div className="w-6 h-6 rounded-md bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                      <Layout size={12} className="text-blue-400" />
                    </div>
                    <span className="text-xs font-semibold text-slate-300">Pages</span>
                    <span className="text-[10px] text-slate-600 bg-white/[0.03] px-1.5 py-0.5 rounded">{parsedPages.length}</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {parsedPages.map((page, i) => (
                      <motion.span
                        key={i}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.03 }}
                        className="tag-chip"
                      >
                        <Layout size={10} className="text-blue-400/60" />
                        {page}
                      </motion.span>
                    ))}
                  </div>
                </div>
              )}

              {parsedEntities.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2.5">
                    <div className="w-6 h-6 rounded-md bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                      <Database size={12} className="text-emerald-400" />
                    </div>
                    <span className="text-xs font-semibold text-slate-300">Entities</span>
                    <span className="text-[10px] text-slate-600 bg-white/[0.03] px-1.5 py-0.5 rounded">{parsedEntities.length}</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {parsedEntities.map((entity, i) => (
                      <motion.span
                        key={i}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.03 }}
                        className="tag-chip"
                      >
                        <Database size={10} className="text-emerald-400/60" />
                        {entity}
                      </motion.span>
                    ))}
                  </div>
                </div>
              )}

              {parsedFlow.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2.5">
                    <div className="w-6 h-6 rounded-md bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                      <GitBranch size={12} className="text-purple-400" />
                    </div>
                    <span className="text-xs font-semibold text-slate-300">Flow</span>
                    <span className="text-[10px] text-slate-600 bg-white/[0.03] px-1.5 py-0.5 rounded">{parsedFlow.length}</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {parsedFlow.map((flow, i) => (
                      <motion.span
                        key={i}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.03 }}
                        className="tag-chip"
                      >
                        <GitBranch size={10} className="text-purple-400/60" />
                        {flow}
                      </motion.span>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center py-12 px-4"
            >
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-white/[0.06] flex items-center justify-center mb-4">
                <FileText size={24} className="text-slate-500" />
              </div>
              <p className="text-sm text-slate-400 font-medium mb-1">No specification yet</p>
              <p className="text-xs text-slate-600 text-center max-w-xs">
                Fill in the form to see a live preview of your specification.
              </p>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
