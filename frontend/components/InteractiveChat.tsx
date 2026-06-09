"use client";

import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Download, Loader2, FileText, CheckCircle } from "lucide-react";

type BackendOption = "Express.js" | "FastAPI" | "Frontend Only";
type FrontendOption = "React" | "Vue";
type DatabaseOption = "MongoDB" | "PostgreSQL" | "None";

export default function InteractiveChat() {
  const [projectName, setProjectName] = useState("");
  const [description, setDescription] = useState("");
  const [pages, setPages] = useState("");
  const [mainFlow, setMainFlow] = useState("");
  const [entities, setEntities] = useState("");
  const [backend, setBackend] = useState<BackendOption>("Express.js");
  const [frontend, setFrontend] = useState<FrontendOption>("React");
  const [database, setDatabase] = useState<DatabaseOption>("MongoDB");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationResult, setGenerationResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const isFrontendOnly = backend === "Frontend Only";

  const parsed = useMemo(() => {
    const pagesList = pages
      .split(/[\n,]+/)
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    const entityList = entities
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .map((line) => {
        const [name, ...rest] = line.split(":").map((s) => s.trim());
        const fields = rest
          .join(":")
          .split(",")
          .map((s) => s.trim())
          .filter((s) => s.length > 0);
        return { name, fields };
      })
      .filter((e) => e.name);

    const stack = isFrontendOnly
      ? frontend
      : `${backend} + ${frontend} + ${database}`;

    return { projectName: projectName || "Untitled", pages: pagesList, entities: entityList, stack };
  }, [projectName, pages, entities, backend, frontend, database, isFrontendOnly]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    setError(null);
    setGenerationResult(null);

    try {
      const body = {
        project_name: projectName,
        description,
        pages: parsed.pages,
        main_flow: mainFlow,
        entities_fields: entities,
        backend_framework: backend,
        frontend_framework: frontend,
        database: isFrontendOnly ? "None" : database,
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
      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
        selected === label
          ? "bg-blue-600 text-white shadow-sm"
          : "bg-slate-800/50 text-slate-400 hover:text-slate-200 border border-slate-700/50"
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
      {/* ── Left: Form ── */}
      <div className="glass-dark p-6 overflow-y-auto max-h-[720px]">
        <motion.h2
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-lg font-semibold gradient-text mb-6"
        >
          SRS Generator
        </motion.h2>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Project Name */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Project Name</label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="e.g. GST Manager"
              className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-400/30 focus:border-blue-400/30 transition-colors"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Project Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe what your project does..."
              rows={3}
              className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-400/30 focus:border-blue-400/30 resize-none transition-colors"
            />
          </div>

          {/* Pages */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Pages</label>
            <textarea
              value={pages}
              onChange={(e) => setPages(e.target.value)}
              placeholder="One per line or comma separated"
              rows={3}
              className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-400/30 focus:border-blue-400/30 resize-none transition-colors"
            />
          </div>

          {/* Main Flow */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Main Flow</label>
            <textarea
              value={mainFlow}
              onChange={(e) => setMainFlow(e.target.value)}
              placeholder={`Describe what a user does step by step.
Example:
1. User opens app and sees pending tasks
2. User fills form to add a new task
3. User clicks 'Mark Complete' on a task
4. Task moves to Completed Tasks page`}
              rows={3}
              className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-400/30 focus:border-blue-400/30 resize-none transition-colors"
            />
          </div>

          {/* Entities & Fields */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Entities & Fields</label>
            <textarea
              value={entities}
              onChange={(e) => setEntities(e.target.value)}
              placeholder={`List your data models and their fields.
Example:
Task: title, description, completed, createdAt
User: name, email, password`}
              rows={3}
              className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-400/30 focus:border-blue-400/30 resize-none transition-colors"
            />
            <p className="text-xs text-slate-500 mt-1">These become your database models. Each line = one model.</p>
          </div>

          {/* Backend */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Backend</label>
            <div className="flex gap-2 flex-wrap">
              {(["Express.js", "FastAPI", "Frontend Only"] as const).map((o) =>
                renderOption(o, backend, setBackend),
              )}
            </div>
          </div>

          {/* Frontend */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Frontend</label>
            <div className="flex gap-2">
              {(["React", "Vue"] as const).map((o) =>
                renderOption(o, frontend, setFrontend),
              )}
            </div>
          </div>

          {/* Database (hidden when Frontend Only) */}
          {!isFrontendOnly && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
            >
              <label className="block text-sm font-medium text-slate-300 mb-2">Database</label>
              <div className="flex gap-2">
                {(["MongoDB", "PostgreSQL", "None"] as const).map((o) =>
                  renderOption(o, database, setDatabase),
                )}
              </div>
            </motion.div>
          )}

          {/* Error */}
          {error && (
            <div className="text-red-400 text-xs bg-red-900/20 border border-red-800/30 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={isGenerating}
            className="w-full btn-primary flex items-center justify-center gap-2 py-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <FileText size={16} />
                Generate Project
              </>
            )}
          </button>

          {/* Results: SRS quality + download */}
          {generationResult && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-3 bg-slate-900/50 border border-slate-700/30 rounded-lg space-y-3"
            >
              {/* Score badge */}
              {generationResult.srs_score !== undefined && (
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold ${
                      generationResult.srs_score >= 71
                        ? "bg-green-900/40 text-green-400 border border-green-700/40"
                        : generationResult.srs_score >= 41
                          ? "bg-yellow-900/40 text-yellow-400 border border-yellow-700/40"
                          : "bg-red-900/40 text-red-400 border border-red-700/40"
                    }`}
                  >
                    {generationResult.srs_score}/100
                  </span>
                  <span className="text-xs text-slate-400">SRS Quality</span>
                </div>
              )}

              {/* Feedback */}
              {generationResult.srs_feedback && (
                <p className="text-xs text-slate-300 leading-relaxed">
                  {generationResult.srs_feedback}
                </p>
              )}

              {/* Missing items */}
              {generationResult.srs_missing?.length > 0 && (
                <div className="space-y-0.5">
                  <p className="text-xs text-slate-500 font-medium">Suggestions:</p>
                  {generationResult.srs_missing.map((item: string, i: number) => (
                    <p key={i} className="text-xs text-slate-400 pl-2 border-l border-slate-700/50">
                      {item}
                    </p>
                  ))}
                </div>
              )}

              <div className="pt-1">
                <p className="text-xs text-slate-400 mb-2">
                  <CheckCircle size={14} className="inline text-green-400 mr-1" />
                  {generationResult.files_generated} files written
                </p>
                {generationResult?.zip_filename && (
                  <a
                    href={`http://localhost:8000/download/${generationResult.zip_filename}`}
                    download
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs transition-colors"
                  >
                    <Download size={14} /> Download ZIP
                  </a>
                )}
              </div>
            </motion.div>
          )}
        </form>
      </div>

      {/* ── Right: Live SRS Preview ── */}
      <div className="glass-dark p-6 overflow-y-auto max-h-[720px]">
        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-5">
          SRS Preview
        </h3>

        <div className="space-y-4 text-sm">
          <div>
            <span className="text-blue-300 font-medium">Project:</span>{" "}
            <span className="text-slate-200">{parsed.projectName}</span>
          </div>

          {parsed.pages.length > 0 && (
            <div>
              <span className="text-blue-300 font-medium">Pages:</span>{" "}
              <span className="text-slate-200">{parsed.pages.join(", ")}</span>
            </div>
          )}

          {parsed.entities.length > 0 && (
            <div>
              <span className="text-blue-300 font-medium">Entities:</span>
              <div className="mt-1 space-y-0.5">
                {parsed.entities.map((e, i) => (
                  <div key={i} className="text-slate-200">
                    <span className="text-amber-300">{e.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="pt-3 border-t border-slate-700/30">
            <span className="text-blue-300 font-medium">Stack:</span>{" "}
            <span className="text-slate-200">{parsed.stack}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
