from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict
import structlog

from ..llm.client import LLMClient, OpenAILLMClient

log = structlog.get_logger()

ROUTE_TOOL = {
    "type": "function",
    "function": {
        "name": "route_message",
        "description": "Classify the incoming message for the best agent.",
        "parameters": {
            "type": "object",
            "properties": {
                "route": {"type": "string", "enum": ["MathAgent", "KnowledgeAgent"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "reason": {"type": "string"}
            },
            "required": ["route"],
            "additionalProperties": False
        }
    }
}

SYSTEM_PROMPT = (
    "You are a router for a modular chatbot. Choose the best agent for the user's message:\n"
    "- MathAgent: arithmetic, calculations, numeric expressions (natural language or symbolic).\n"
    "- KnowledgeAgent: product/FAQ questions from InfinitePay help center.\n"
    "If it's math-like, prefer MathAgent; otherwise, KnowledgeAgent.\n"
    "Call the tool route_message with your decision."
)

@dataclass
class RouterAgentLLM:
    llm: LLMClient | None = None
    name: str = "RouterAgent"

    def __post_init__(self):
        if self.llm is None:
            self.llm = OpenAILLMClient()

    def decide(self, message: str) -> Dict[str, Any]:
        args = self.llm.call_tool(
            system=SYSTEM_PROMPT,
            user=f"User message:\n{message.strip()}",
            tools=[ROUTE_TOOL],
            tool_choice="auto",
        )
        if not isinstance(args, dict) or "route" not in args:
            route = "MathAgent" if any(t in message.lower() for t in ["+", "-", "*", "/", " x ", "vezes", "quanto é"]) else "KnowledgeAgent"
            args = {"route": route, "confidence": 0.5, "reason": "fallback_rule"}
        log.bind(level="INFO", agent=self.name, decision=args.get("route"), confidence=args.get("confidence"), reason=args.get("reason")).msg("route_decision")
        log.bind(level="DEBUG", agent="RouterAgent", out_args=args).msg("router_llm_raw")
        return args
