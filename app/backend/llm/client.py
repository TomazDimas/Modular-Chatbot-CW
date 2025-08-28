from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Protocol, Dict, Any, List

class LLMClient(Protocol):
    def generate(self, system: str, user: str) -> str: ...
    def generate_json(self, system: str, user: str) -> Dict[str, Any]: ...
    def call_tool(self, system: str, user: str, tools: List[Dict[str, Any]], tool_choice: str = "auto") -> Dict[str, Any]: ...

@dataclass
class OpenAILLMClient:
    api_key: str | None = None
    model: str = os.getenv("MATH_LLM_MODEL", "gpt-4o-mini")

    def __post_init__(self):
        self.api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY não configurada")

        from openai import OpenAI
        self._client = OpenAI(api_key=self.api_key)

    def _base(self, system: str, user: str) -> list[dict]:
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    def generate(self, system: str, user: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=self._base(system, user),
            temperature=0,
        )
        return resp.choices[0].message.content or ""

    def generate_json(self, system: str, user: str) -> Dict[str, Any]:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=self._base(system, user),
            temperature=0,
            response_format={"type": "json_object"},
        )
        import json
        try:
            return json.loads(resp.choices[0].message.content or "{}")
        except json.JSONDecodeError:
            return {}

    def call_tool(self, system: str, user: str, tools: List[Dict[str, Any]], tool_choice: str = "auto") -> Dict[str, Any]:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=self._base(system, user),
            tools=tools,
            tool_choice=tool_choice,
            temperature=0,
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return {}
        call = msg.tool_calls[0]
        import json
        return json.loads(call.function.arguments)
