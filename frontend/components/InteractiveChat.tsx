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
  onPlanArchitecture: (validationData: any) => Promise<void>;
}

export default function InteractiveChat({
  onValidationComplete,
  addLog,
  phase,
  onPlanArchitecture,
}: InteractiveChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "agent",
      text: "Hey! I'm your AI architecture assistant. Tell me about your project idea, and I'll help you plan the perfect full-stack architecture.",
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
    if (validationData) {
      addMessage("agent", "Validation is complete, so I am using that stack to generate the architecture now.");
      return;
    }

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

    // Instead of hardcoded replies, call backend /chat to get Llama-generated responses for conversational intents
    const lowerInput = userInput.toLowerCase();
    const conversationalTriggers = ["confused", "i'm confused", "im confused", "what would you suggest", "what do you suggest", "suggest"];
    const isConversational = conversationalTriggers.some((t) => lowerInput.includes(t));

    if (isConversational) {
      try {
        addLog("info", "→ Asking Llama for conversational reply...");
        const chatResp = await fetch("http://localhost:8000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: userInput, conversation: updatedConversation }),
        });

        if (!chatResp.ok) throw new Error("Chat API error");
        const json = await chatResp.json();
        const reply = json.reply || "Sorry, I couldn't generate a reply.";
        addMessage("agent", reply);
        setConversation((prev) => [...prev, { role: "agent", content: reply }]);
        setIsLoading(false);
        return;
      } catch (err) {
        addLog("error", `✗ Chat error: ${err}`);
        addMessage("agent", "Sorry, I couldn't reach the chat service. Please try again.");
        setIsLoading(false);
        return;
      }
    }

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
          onPlanArchitecture(data);
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

  const isDisabled = isLoading || phase !== "chat" || Boolean(validationData);

  return (
    <div className="bg-slate-950/30 backdrop-blur-sm h-full max-h-[720px] flex flex-col text-slate-200">
      {/* Chat Header */}
      <div className="px-4 py-3 flex items-center gap-2">
        <MessageCircle size={18} className="text-blue-300" />
        <h2 className="font-semibold text-slate-100">Interactive Chat</h2>
      </div>

      {/* Messages */}
      <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-3">
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
                className={`max-w-xs lg:max-w-sm px-3 py-2 rounded-md shadow-sm ${
                  msg.type === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-800/90 text-slate-200"
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
      <div className="pt-3 px-3 pb-4">
        <div className="flex gap-2 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isDisabled}
            placeholder={validationData ? "Architecture planning is in progress..." : isDisabled ? "Waiting for validation..." : "Type your message..."}
            className="flex-1 h-20 max-h-24 overflow-y-auto bg-transparent border border-slate-800/40 rounded-md px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-400/30 disabled:opacity-50 resize-none"
            rows={2}
          />
          <button
            onClick={handleSend}
            disabled={isDisabled || !input.trim()}
            className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={16} />
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-2">Shift+Enter for new line</p>
      </div>
    </div>
  );
}
