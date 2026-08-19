import { useEffect, useRef, useState, type FormEvent } from "react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Alert } from "../components/Alert";
import { useAuth } from "../context/AuthContext";
import { ApiError, streamChat } from "../lib/api";

interface ToolEvent {
  name: string;
  args?: Record<string, unknown>;
  result?: string;
  status: "calling" | "done";
}

interface DisplayMessage {
  role: "user" | "assistant";
  content: string;
  tools: ToolEvent[];
}

const SUGGESTIONS = [
  "What's my savings balance?",
  "Transfer $20 to account 10000001",
  "Close my current account",
];

export function ChatPage() {
  const { profile } = useAuth();
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const historyRef = useRef<{ role: "user" | "assistant"; content: string }[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function sendMessage(text: string) {
    if (!profile || !text.trim() || sending) return;
    setError(null);
    setSending(true);

    const priorHistory = [...historyRef.current];
    setMessages((prev) => [
      ...prev,
      { role: "user", content: text, tools: [] },
      { role: "assistant", content: "", tools: [] },
    ]);
    setInput("");

    let assistantContent = "";

    function updateAssistant(mutate: (msg: DisplayMessage) => DisplayMessage) {
      setMessages((prev) => {
        const next = [...prev];
        const lastIndex = next.length - 1;
        next[lastIndex] = mutate(next[lastIndex]);
        return next;
      });
    }

    try {
      for await (const evt of streamChat(text, priorHistory, profile.token)) {
        if (evt.event === "token") {
          const content = (evt.data as { content: string }).content;
          assistantContent += content;
          updateAssistant((msg) => ({ ...msg, content: msg.content + content }));
        } else if (evt.event === "tool_call") {
          const { name, args } = evt.data as { name: string; args: Record<string, unknown> };
          updateAssistant((msg) => ({
            ...msg,
            tools: [...msg.tools, { name, args, status: "calling" }],
          }));
        } else if (evt.event === "tool_result") {
          const { name, content } = evt.data as { name: string; content: string };
          updateAssistant((msg) => {
            const tools = [...msg.tools];
            const idx = tools.findIndex((t) => t.name === name && t.status === "calling");
            if (idx !== -1) tools[idx] = { ...tools[idx], status: "done", result: content };
            return { ...msg, tools };
          });
        } else if (evt.event === "error") {
          const detail = (evt.data as { detail: string }).detail;
          setError(detail);
        }
      }
      historyRef.current = [
        ...priorHistory,
        { role: "user", content: text },
        { role: "assistant", content: assistantContent },
      ];
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "The assistant is unavailable right now.");
    } finally {
      setSending(false);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    sendMessage(input);
  }

  return (
    <div className="flex h-[calc(100vh-9rem)] flex-col">
      <div className="mb-4">
        <h1 className="text-2xl font-extrabold text-ink-900">AI Assistant</h1>
        <p className="mt-1 text-sm text-ink-500">
          Ask about your balance, send money, or close an account — securely, using your own login.
        </p>
      </div>

      {error && (
        <div className="mb-4">
          <Alert tone="error">{error}</Alert>
        </div>
      )}

      <Card className="flex flex-1 flex-col overflow-hidden p-0">
        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-6">
          {messages.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
              <span className="text-4xl">🤖</span>
              <p className="text-sm text-ink-500">Try asking one of these:</p>
              <div className="flex flex-wrap justify-center gap-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => sendMessage(s)}
                    className="rounded-full border border-ink-200 bg-white px-3 py-1.5 text-xs font-medium text-ink-600 hover:bg-ink-50"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] ${msg.role === "user" ? "items-end" : "items-start"} flex flex-col gap-2`}>
                {msg.tools.map((tool, ti) => (
                  <div
                    key={ti}
                    className="flex items-center gap-2 rounded-lg bg-brand-50 px-3 py-1.5 text-xs font-medium text-brand-700"
                  >
                    <span>{tool.status === "calling" ? "⏳" : "✅"}</span>
                    <span>
                      {tool.status === "calling" ? "Calling" : "Called"} <code>{tool.name}</code>
                    </span>
                  </div>
                ))}
                {(msg.content || msg.role === "assistant") && (
                  <div
                    className={`rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap ${
                      msg.role === "user"
                        ? "bg-brand-600 text-white"
                        : "bg-ink-100 text-ink-900"
                    }`}
                  >
                    {msg.content || (sending && i === messages.length - 1 ? "…" : "")}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
        <form onSubmit={handleSubmit} className="flex gap-2 border-t border-ink-100 p-4">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your accounts…"
            disabled={sending}
            className="flex-1 rounded-xl border border-ink-200 bg-white px-3.5 py-2.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100 disabled:bg-ink-50"
          />
          <Button type="submit" loading={sending} disabled={!input.trim()}>
            Send
          </Button>
        </form>
      </Card>
    </div>
  );
}
