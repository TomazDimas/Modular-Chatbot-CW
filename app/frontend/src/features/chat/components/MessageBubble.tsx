import type { HistoryItem } from "../types";

export default function MessageBubble({ msg }: { msg: HistoryItem }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[78%] rounded-2xl px-4 py-3 shadow-soft border ${
          isUser
            ? "bg-accent/20 border-accent/40"
            : "bg-[#0f172a] border-[#1f2937]"
        }`}
      >
        {!isUser && msg.agent && (
          <div className="text-[10px] uppercase tracking-wide text-subtle mb-1">
            {msg.agent}
          </div>
        )}
        <div className="whitespace-pre-wrap leading-relaxed text-left">
          {msg.content}
        </div>
        {!isUser && msg._sources && (
          <div className="mt-2 text-xs text-subtle">
            <span className="opacity-70 mr-1">Sources:</span>
            <span className="underline underline-offset-2 break-all">
              {msg._sources}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
