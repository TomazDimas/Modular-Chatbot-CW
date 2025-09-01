import { useMutation, useQueryClient } from "@tanstack/react-query";
import { conversationKey } from "./useConversation";
import type { ChatRequest, HistoryItem } from "../types";
import { sendChat } from "../../../api/chat";

export function useSendMessage(convId: string, userId: string) {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (payload: ChatRequest) => sendChat(payload),
    onSuccess: (res) => {
      const agent = res.agent_workflow?.at(-1)?.agent as
        | HistoryItem["agent"]
        | undefined;
      const sources = res.source_agent_response?.startsWith("Sources:")
        ? res.source_agent_response.replace(/^Sources:\s*/i, "")
        : undefined;
      const assistant: HistoryItem = {
        role: "assistant",
        content: res.response,
        agent,
        _sources: sources,
      };

      qc.setQueryData<HistoryItem[]>(conversationKey(convId), (old) => [
        ...(old ?? []),
        assistant,
      ]);
    },
  });
}
