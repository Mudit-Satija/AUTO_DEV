"use client";

import { motion } from "framer-motion";
import { Download, RefreshCw, Database, Zap, Code, Shield } from "lucide-react";

interface ArchitectureResultProps {
  data: any;
  onNewProject: () => void;
}

export default function ArchitectureResult({ data, onNewProject }: ArchitectureResultProps) {
  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    element.href = URL.createObjectURL(file);
    element.download = `architecture_output_${Date.now()}.json`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      {/* Header */}
      <div className="glass p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold gradient-text mb-1">Backend Architecture Plan</h2>
            <p className="text-sm text-slate-400">Generated AI-optimized architecture for your project</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleDownload}
            className="btn-primary flex items-center gap-2"
          >
            <Download size={16} />
            Download JSON
          </motion.button>
        </div>

        {/* Reasoning */}
        <div className="bg-slate-900/50 border border-slate-700/30 rounded-lg p-4 mt-4">
          <p className="text-xs text-slate-400 mb-2 uppercase tracking-wider font-semibold">
            Reasoning
          </p>
          <p className="text-sm text-slate-300 leading-relaxed">{data.reasoning}</p>
        </div>
      </div>

      {/* Core Information Grid */}
      <div className="grid grid-cols-2 gap-4">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass p-4">
          <Code size={20} className="text-blue-400 mb-2" />
          <p className="text-xs text-slate-400 mb-1">Framework</p>
          <p className="font-semibold text-slate-100">{data.framework}</p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass p-4">
          <Zap size={20} className="text-cyan-400 mb-2" />
          <p className="text-xs text-slate-400 mb-1">Language</p>
          <p className="font-semibold text-slate-100">{data.language}</p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass p-4">
          <Database size={20} className="text-purple-400 mb-2" />
          <p className="text-xs text-slate-400 mb-1">Database</p>
          <p className="font-semibold text-slate-100">{data.database.type}</p>
          <p className="text-xs text-slate-500 mt-1">{data.database.orm}</p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="glass p-4">
          <Shield size={20} className="text-green-400 mb-2" />
          <p className="text-xs text-slate-400 mb-1">Auth Method</p>
          <p className="font-semibold text-slate-100">{data.authentication.method}</p>
        </motion.div>
      </div>

      {/* Authentication Details */}
      <div className="glass p-6">
        <h3 className="text-lg font-semibold mb-4 gradient-text">Authentication Strategy</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-slate-400 mb-1 uppercase tracking-wider">Storage</p>
            <p className="text-sm font-medium text-slate-200">{data.authentication.storage}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400 mb-1 uppercase tracking-wider">Refresh Strategy</p>
            <p className="text-sm font-medium text-slate-200">{data.authentication.refresh_strategy}</p>
          </div>
        </div>
        {data.authentication.libraries && (
          <div className="mt-4 pt-4 border-t border-slate-700/30">
            <p className="text-xs text-slate-400 mb-2 uppercase tracking-wider">Libraries</p>
            <div className="flex flex-wrap gap-2">
              {data.authentication.libraries.map((lib: string, idx: number) => (
                <span key={idx} className="text-xs bg-blue-900/30 border border-blue-700/50 text-blue-300 px-2.5 py-1 rounded">
                  {lib}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* API Endpoints */}
      {data.suggested_endpoints && (
        <div className="glass p-6">
          <h3 className="text-lg font-semibold mb-4 gradient-text">Suggested API Endpoints</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {data.suggested_endpoints.slice(0, 8).map((endpoint: any, idx: number) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="flex items-start gap-3 p-3 bg-slate-900/30 border border-slate-700/30 rounded"
              >
                <span className={`text-xs font-bold px-2 py-1 rounded flex-shrink-0 ${
                  endpoint.method === "GET" ? "bg-blue-900/50 text-blue-300" :
                  endpoint.method === "POST" ? "bg-green-900/50 text-green-300" :
                  endpoint.method === "PUT" ? "bg-yellow-900/50 text-yellow-300" :
                  "bg-red-900/50 text-red-300"
                }`}>
                  {endpoint.method}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-mono text-slate-300 truncate">{endpoint.path}</p>
                  <p className="text-xs text-slate-400">{endpoint.description}</p>
                </div>
                {endpoint.auth_required && (
                  <Shield size={14} className="text-yellow-500 flex-shrink-0 mt-1" />
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Libraries */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="glass p-6">
          <h3 className="text-sm font-semibold mb-3 text-slate-300 uppercase tracking-wider">Core Libraries</h3>
          <div className="flex flex-wrap gap-2">
            {data.core_libraries?.map((lib: string, idx: number) => (
              <span key={idx} className="text-xs bg-slate-900/50 border border-slate-700/50 text-slate-300 px-2.5 py-1 rounded">
                {lib}
              </span>
            ))}
          </div>
        </div>

        <div className="glass p-6">
          <h3 className="text-sm font-semibold mb-3 text-slate-300 uppercase tracking-wider">Design Patterns</h3>
          <div className="flex flex-wrap gap-2">
            {data.design_patterns?.map((pattern: string, idx: number) => (
              <span key={idx} className="text-xs bg-purple-900/30 border border-purple-700/50 text-purple-300 px-2.5 py-1 rounded">
                {pattern}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Folder Structure */}
      {data.folder_structure && (
        <div className="glass p-6">
          <h3 className="text-lg font-semibold mb-4 gradient-text">Recommended Folder Structure</h3>
          <div className="space-y-2 font-mono text-sm">
            {data.folder_structure.map((item: any, idx: number) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="text-slate-300"
              >
                <span className="text-blue-400">{item.name}</span>
                {item.description && (
                  <span className="text-slate-500 ml-2">// {item.description}</span>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-4 pt-4 border-t border-slate-800/50">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onNewProject}
          className="btn-secondary flex items-center gap-2 flex-1"
        >
          <RefreshCw size={16} />
          Start New Project
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleDownload}
          className="btn-primary flex items-center gap-2 flex-1"
        >
          <Download size={16} />
          Download Plan
        </motion.button>
      </div>
    </motion.div>
  );
}
