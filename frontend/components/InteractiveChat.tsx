"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, MessageCircle } from "lucide-react";

interface Message {
  id: string;
  type: "user" | "agent";
  text: string;
  isTyping?: boolean;
}

interface InteractiveChatProps {
  onValidationComplete: (data: any) => void;
  addLog: (type: string, text: string) => void;
  phase: string;
  onPlanFrontend: (validationData: any) => Promise<void>;
}

export default function InteractiveChat({
  onValidationComplete,
  addLog,
  phase,
  onPlanFrontend,
}: InteractiveChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "agent",
      text: "Hey! 👋 I'm your AI architecture assistant. Tell me about your project idea, and I'll help you plan the perfect backend architecture.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversation, setConversation] = useState<Array<{ role: string; content: string }>>([]);
  const [validationData, setValidationData] = useState<any>(null);
  const [projectPrompt, setProjectPrompt] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const addMessage = (type: "user" | "agent", text: string, isTyping = false) => {
    setMessages((prev) => [...prev, {
      id: Math.random().toString(),
      type,
      text,
      isTyping,
    }]);
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message
    addMessage("user", input);
    const userInput = input;
    setInput("");
    setIsLoading(true);

    if (!projectPrompt) {
      setProjectPrompt(userInput);
    }

    // Update conversation history
    const updatedConversation = [
      ...conversation,
      { role: "user", content: userInput },
    ];
    setConversation(updatedConversation);

    try {
      // Call interactive validation endpoint
      addLog("info", "→ Sending validation request...");

      const response = await fetch("http://localhost:8000/validate-interactive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: projectPrompt || userInput,
          conversation: updatedConversation,
        }),
      });

      if (!response.ok) throw new Error("API error");

      const data = await response.json();
      addLog("info", "← Response received");

      if (data.status === "success") {
        addMessage("agent", data.feedback || "Validation complete.");
        setConversation((prev) => [
          ...prev,
          { role: "agent", content: data.feedback || "Validation complete." },
        ]);
        addLog("success", "✓ Validation complete!");
        setValidationData(data);
        onValidationComplete(data);
        
        setTimeout(() => {
          onPlanFrontend(data);
        }, 1000);
      } else if (data.current_question) {
        addMessage("agent", data.current_question);
        setConversation((prev) => [
          ...prev,
          { role: "agent", content: data.current_question },
        ]);
      }
    } catch (error) {
      addLog("error", `✗ Error: ${error}`);
      addMessage("agent", "Sorry, I encountered an error. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const isDisabled = isLoading || phase !== "chat";

  return (
    <div className="glass h-full max-h-[800px] flex flex-col">
      {/* Chat Header */}
      <div className="border-b border-slate-700/30 px-4 py-3 flex items-center gap-2">
        <MessageCircle size={18} className="text-blue-400" />
        <h2 className="font-semibold text-slate-100">Interactive Chat</h2>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-xs lg:max-w-sm px-4 py-2.5 rounded-lg ${
                  msg.type === "user"
                    ? "bg-blue-600/50 border border-blue-500/50 text-slate-100"
                    : "bg-slate-800/50 border border-slate-700/50 text-slate-300"
                }`}
              >
                <p className="text-sm leading-relaxed">
                  {msg.isTyping ? (
                    <span className="animate-typing inline-block">
                      {msg.text.slice(0, 20)}...
                    </span>
                  ) : (
                    msg.text
                  )}
                </p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-2"
          >
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ delay: i * 0.1, repeat: Infinity, duration: 0.8 }}
                className="w-2 h-2 bg-blue-400 rounded-full"
              />
            ))}
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-slate-700/30 p-4 space-y-3">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isDisabled}
            placeholder={isDisabled ? "Waiting for validation..." : "Type your message..."}
            className="flex-1 bg-slate-900/50 border border-slate-700/50 rounded-lg px-3 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500/50 disabled:opacity-50 resize-none"
            rows={2}
          />
          <button
            onClick={handleSend}
            disabled={isDisabled || !input.trim()}
            className="btn-primary flex items-center gap-2 self-end disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={16} />
          </button>
        </div>
        <p className="text-xs text-slate-500">Shift+Enter for new line</p>
      </div>
    </div>
  );
}
