import type { HistoryItem } from "../types";
import MessageBubble from "./MessageBubble";
import { useEffect, useRef } from "react";

export default function ChatWindow({
  history,
  pending,
}: {
  history: HistoryItem[];
  pending?: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    ref.current?.scrollTo({
      top: ref.current.scrollHeight,
      behavior: "smooth",
    });
  }, [history.length, pending]);

  return (
    <div
      ref={ref}
      className="flex-1 overflow-y-auto p-4 rounded-xl2 bg-card border border-[#1f2937]"
    >
      <div className="flex flex-col gap-3">
        {history.map((m, i) => (
          <MessageBubble key={i} msg={m} />
        ))}
        {pending && <div className="text-subtle text-sm italic">Thinking…</div>}
      </div>
    </div>
  );
}
