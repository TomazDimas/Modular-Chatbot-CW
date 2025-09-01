import { v4 as uuidv4 } from "uuid";

export default function ConversationHeader({
  conversationId,
  setConversationId,
  onRefresh,
  recent = [],
}: {
  conversationId: string;
  setConversationId: (v: string) => void;
  onRefresh: () => void;
  recent?: string[];
}) {
  return (
    <div className="flex items-center gap-3 p-3 bg-card rounded-xl2 shadow-soft">
      <div className="flex flex-col w-full">
        <label className="text-xs text-subtle">Conversation ID</label>
        <input
          className="mt-1 w-full rounded-lg bg-[#0f172a] border border-[#1f2937] px-3 py-2 outline-none focus:border-accent"
          value={conversationId}
          onChange={(e) => setConversationId(e.target.value.trim())}
          placeholder="conv-1234"
        />
        {recent.length > 0 && (
          <div className="mt-1 text-xs text-subtle flex gap-2 flex-wrap">
            Recent:
            {recent.map((id) => (
              <button
                key={id}
                onClick={() => setConversationId(id)}
                className="px-2 py-0.5 rounded bg-[#1f2937] hover:bg-[#374151]"
              >
                {id.slice(0, 8)}…
              </button>
            ))}
          </div>
        )}
      </div>
      <button
        onClick={() => setConversationId(uuidv4())}
        className="px-4 py-2 rounded-lg bg-[#1f2937] hover:bg-[#374151] transition"
      >
        New
      </button>
      <button
        onClick={onRefresh}
        className="px-4 py-2 rounded-lg bg-accent/20 border border-accent/40 hover:bg-accent/30 transition"
      >
        Refresh
      </button>
    </div>
  );
}
