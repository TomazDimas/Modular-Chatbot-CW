import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createConversation,
  deleteConversation,
  listConversations,
} from "../../../api/chat";

export const conversationsKey = (userId: string) => ["conversations", userId];

export function useConversationsList(userId: string) {
  const qc = useQueryClient();

  const listQ = useQuery({
    queryKey: conversationsKey(userId),
    queryFn: () => listConversations(userId),
    enabled: !!userId,
  });

  const createM = useMutation({
    mutationFn: () => createConversation(userId),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: conversationsKey(userId) });
    },
  });

  const deleteM = useMutation({
    mutationFn: (conversationId: string) =>
      deleteConversation(userId, conversationId),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: conversationsKey(userId) });
    },
  });

  return { ...listQ, createM, deleteM };
}
