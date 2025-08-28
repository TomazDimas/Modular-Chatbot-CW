from __future__ import annotations
import re, time, json, structlog
from dataclasses import dataclass
from typing import Any, Dict, List

from ..llm.client import LLMClient, OpenAILLMClient
from .math_parser import eval_expr, MathError

log = structlog.get_logger()

MATH_ALLOWED = re.compile(r"^[\d\.\s\+\-\*\/\(\)]+$")

EXTRACT_EXPRESSION_TOOL: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "extract_expression",
        "description": "Extract a simple arithmetic expression from the user's request.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": 'Only numbers, spaces, "+-*/()", and dots for decimals.',
                    "pattern": r"^[\d\.\s\+\-\*\/\(\)]+$"
                },
                "answer": {
                    "type": "number",
                    "description": "Optional numeric result if trivial; the server will validate anyway."
                }
            },
            "required": ["expression"],
            "additionalProperties": False
        }
    }
}

SYSTEM_PROMPT = (
    "You are a math router/translator. If the user's message asks to compute an arithmetic expression, "
    "call the tool extract_expression with a minimal expression (only numbers, spaces, '+-*/()' and dots). "
    "If the message is NOT a math query, do not call any tool."
)

USER_TEMPLATE = "User message:\n{message}"

@dataclass
class MathAgentLLM:
    llm: LLMClient | None = None
    name: str = "MathAgent"

    def __post_init__(self):
        if self.llm is None:
            self.llm = OpenAILLMClient()

    def _extract_with_tools(self, message: str) -> Dict[str, Any]:
        args = self.llm.call_tool(
            system=SYSTEM_PROMPT,
            user=USER_TEMPLATE.format(message=message.strip()),
            tools=[EXTRACT_EXPRESSION_TOOL],
            tool_choice="auto",
        )
        return args 

    def _extract_with_json(self, message: str) -> Dict[str, Any]:
        system = (
            "Output JSON only. Keys: expression (string with only numbers/spaces '+-*/()' and dots), "
            "and optional answer (number). If not a math query, return {\"error\":\"not_math\"}."
        )
        user = f"User message:\n{message}\n"
        return self.llm.generate_json(system, user)

    def run(self, message: str) -> dict:
        t0 = time.time()

        data: Dict[str, Any] = self._extract_with_tools(message)

        if not data:
            try:
                data = self._extract_with_json(message)
            except Exception:
                data = {}

        if not isinstance(data, dict) or "expression" not in data:
            raise MathError("Isso não parece ser uma expressão matemática simples.")

        expr = str(data["expression"]).strip()

        if not expr or not MATH_ALLOWED.match(expr):
            raise MathError("Expressão inválida.")

        result = eval_expr(expr)

        llm_ms = int((time.time() - t0) * 1000)
        log.bind(level="INFO", agent="MathAgent", expr=expr, result=result, llm_latency_ms=llm_ms).msg("math_llm_ok")

        return {
            "text": f"Resultado: {result}",
            "meta": {"expr": expr, "result": result, "llm_latency_ms": llm_ms},
        }
