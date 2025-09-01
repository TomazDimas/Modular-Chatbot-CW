import { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import ChatWindow from "./components/ChatWindow";
import Composer from "./components/Composer";
import { useConversation } from "./hooks/useConversation";
import { useSendMessage } from "./hooks/useSendMessage";
import type { HistoryItem } from "./types";
import { useConversationsList } from "./hooks/useConversationsList";
import { getOrCreateUserId } from "../../lib/user";

const USER_ID = getOrCreateUserId();

export default function ChatPage() {
  const [conversationId, setConversationId] = useState(
    () => `conv-${uuidv4()}`
  );
  const [sidebarCollapsed, setSidebarCollapsed] = useState(true);

  const {
    data: history = [],
    isFetching,
    appendOptimistic,
    refetch,
  } = useConversation(conversationId);
  const sendMutation = useSendMessage(conversationId, USER_ID);
  const convList = useConversationsList(USER_ID);

  async function onSend(text: string) {
    const userMsg: HistoryItem = {
      role: "user",
      content: text,
      user_id: USER_ID,
    };
    appendOptimistic(userMsg);
    await sendMutation.mutateAsync({
      message: text,
      user_id: USER_ID,
      conversation_id: conversationId,
    });
    convList.refetch?.();
  }

  async function handleDelete(id: string) {
    const ok = confirm("Delete this conversation? This cannot be undone.");
    if (!ok) return;

    await convList.deleteM.mutateAsync(id);

    const remaining = (convList.data ?? []).filter(
      (c) => c.conversation_id !== id
    );
    if (id === conversationId) {
      if (remaining.length > 0) {
        setConversationId(remaining[0].conversation_id);
      } else {
        const res = await convList.createM.mutateAsync();
        setConversationId(res.conversation_id);
      }
    }
    convList.refetch?.();
  }

  return (
    <div className="min-h-full h-screen max-h-screen">
      <header className="h-14 border-b border-[#1f2937] flex items-center px-4 gap-3">
        <button
          className="md:hidden text-subtle"
          onClick={() => setSidebarCollapsed(false)}
        >
          Menu
        </button>
        <h1 className="text-lg font-semibold">InfinitePay Support Chat</h1>
        <div className="ml-auto text-xs text-subtle">
          API: {import.meta.env.VITE_API_BASE}
        </div>
      </header>

      <div className="flex h-[calc(100vh-56px)]">
        <aside
          className={`
            md:static fixed inset-y-14 left-0 z-20 transition-transform
            ${sidebarCollapsed ? "-translate-x-full" : "translate-x-0"}
            md:translate-x-0 w-64 border-r border-[#1f2937] bg-card
          `}
        >
          <div className="flex items-center justify-between p-3">
            <div className="text-sm font-medium">Conversations</div>
            <button
              onClick={async () => {
                const res = await convList.createM.mutateAsync();
                setConversationId(res.conversation_id);
                setSidebarCollapsed(true);
                convList.refetch?.();
              }}
              className="px-2 py-1 rounded bg-[#1f2937] hover:bg-[#374151] text-xs"
            >
              New
            </button>
          </div>

          <div className="px-2 pb-2 space-y-1 overflow-y-auto h-[calc(100%-56px)]">
            {(convList.data ?? []).map((it) => {
              const active = it.conversation_id === conversationId;
              return (
                <div
                  key={it.conversation_id}
                  className={`group relative rounded-lg border ${
                    active
                      ? "bg-accent/20 border-accent/40"
                      : "bg-[#0f172a] border-[#1f2937]"
                  }`}
                >
                  <button
                    onClick={() => {
                      setConversationId(it.conversation_id);
                      setSidebarCollapsed(true);
                    }}
                    className="w-full text-left px-3 py-2 block hover:bg-[#101826] rounded-lg"
                  >
                    <div className="text-sm font-medium truncate">
                      {it.title || it.conversation_id}
                    </div>
                    {it.last_message_preview && (
                      <div className="text-xs text-subtle truncate">
                        {it.last_message_preview}
                      </div>
                    )}
                  </button>

                  <button
                    title="Delete conversation"
                    className="absolute top-2 right-2 text-subtle hover:text-ink text-xs opacity-0 group-hover:opacity-100 md:opacity-0"
                    onClick={(e) => {
                      e.stopPropagation();
                      void handleDelete(it.conversation_id);
                    }}
                  >
                    ✕
                  </button>
                </div>
              );
            })}

            {(!convList.data || convList.data.length === 0) &&
              !convList.isLoading && (
                <div className="text-xs text-subtle px-3 py-2">
                  No conversations yet.
                </div>
              )}
          </div>

          <button
            className="absolute top-2 left-2 md:hidden text-subtle text-xs"
            onClick={() => setSidebarCollapsed(true)}
          >
            Close
          </button>
        </aside>

        <main className="flex-1 flex flex-col p-4 gap-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-subtle truncate">{conversationId}</div>
            <button
              onClick={() => refetch()}
              className="text-xs text-subtle hover:text-ink"
            >
              Refresh
            </button>
          </div>

          <ChatWindow
            history={history}
            pending={isFetching || sendMutation.isPending}
          />

          <Composer onSend={onSend} disabled={sendMutation.isPending} />
        </main>
      </div>
    </div>
  );
}
