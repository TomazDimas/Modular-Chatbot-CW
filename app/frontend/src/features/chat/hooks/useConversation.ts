import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { HistoryItem } from "../types";
import { getConversation } from "../../../api/chat";

export const conversationKey = (id: string) => ["conversation", id];

export function useConversation(convId: string) {
  const qc = useQueryClient();
  const query = useQuery({
    queryKey: conversationKey(convId),
    queryFn: () => getConversation(convId),
    enabled: !!convId,
  });

  const appendOptimistic = (msg: HistoryItem) => {
    qc.setQueryData<HistoryItem[]>(conversationKey(convId), (old) => [
      ...(old ?? []),
      msg,
    ]);
  };

  return { ...query, appendOptimistic };
}
