import type {
  ChatRequest,
  ChatResponseDTO,
  HistoryItem,
} from "../features/chat/types";
import { apiGet, apiPost } from "./client";

export type ConversationMeta = {
  conversation_id: string;
  user_id: string;
  title?: string;
  last_message_preview?: string;
  updated_at?: string;
};

export const getConversation = (id: string) =>
  apiGet<HistoryItem[]>(`/chat/${encodeURIComponent(id)}`);

export const sendChat = (payload: ChatRequest) =>
  apiPost<ChatResponseDTO>("/chat", payload);

export const listConversations = (userId: string) =>
  apiGet<ConversationMeta[]>(
    `/users/${encodeURIComponent(userId)}/conversations`
  );

export const createConversation = (userId: string) =>
  apiPost<{ conversation_id: string }>(
    `/users/${encodeURIComponent(userId)}/conversations`,
    {}
  );

export async function deleteConversation(
  userId: string,
  conversationId: string
) {
  const res = await fetch(
    `${(import.meta.env.VITE_API_BASE || "").replace(
      /\/+$/,
      ""
    )}/users/${encodeURIComponent(userId)}/conversations/${encodeURIComponent(
      conversationId
    )}`,
    { method: "DELETE" }
  );
  if (!res.ok) throw new Error(await res.text().catch(() => "DELETE failed"));
  return res.json() as Promise<{ ok: true }>;
}
