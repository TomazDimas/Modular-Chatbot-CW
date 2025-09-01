export type Role = "user" | "assistant";
export type AgentName = "RouterAgent" | "KnowledgeAgent" | "MathAgent" | "API";

export interface HistoryItem {
  role: Role;
  content: string;
  user_id?: string;
  agent?: AgentName;
  _sources?: string;
}

export interface ChatRequest {
  message: string;
  user_id: string;
  conversation_id: string;
}

export interface AgentStep {
  agent: AgentName;
  decision?: AgentName | null;
}

export interface ChatResponseDTO {
  response: string;
  source_agent_response: string;
  agent_workflow: AgentStep[];
}
