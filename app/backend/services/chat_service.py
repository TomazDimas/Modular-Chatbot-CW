from __future__ import annotations
import json, time, structlog
from typing import List

from ..core.security import MATH_ONLY_REGEX, seems_injection
from ..infra.redis_client import redis_client as r
from ..domain.schemas import AgentStep, ChatRequest, ChatResponse
from ..agents.router_llm import RouterAgentLLM
from ..agents.math_llm import MathAgentLLM
from ..agents.math_parser import MathError
from ..agents.knowledge_redis import KnowledgeAgentRedis

log = structlog.get_logger()

class ChatService:
    @staticmethod
    def handle(req: ChatRequest) -> ChatResponse:
        t0 = time.time()
        workflow: List[AgentStep] = []

        if seems_injection(req.message):
            log.bind(
                level="WARNING",
                agent="RouterAgent",
                conversation_id=req.conversation_id,
                user_id=req.user_id,
                suspicious_input=True,
            ).msg("suspected_prompt_injection")

        t_router = time.time()
        decision = "KnowledgeAgent"
        route_meta = {"confidence": None, "reason": None, "mode": "llm"}

        try:
            router_agent = RouterAgentLLM()
            router_args = router_agent.decide(req.message)

            if isinstance(router_args, dict) and "route" in router_args:
                decision = router_args.get("route", "KnowledgeAgent")
                route_meta["confidence"] = router_args.get("confidence")
                route_meta["reason"] = router_args.get("reason")
            else:
                route_meta["mode"] = "rule_fallback_payload"
                decision = "MathAgent" if MATH_ONLY_REGEX.match(req.message) else "KnowledgeAgent"
        except Exception as e:
            route_meta["mode"] = "rule_fallback_error"
            route_meta["error"] = str(e)
            decision = "MathAgent" if MATH_ONLY_REGEX.match(req.message) else "KnowledgeAgent"

        router_ms = int((time.time() - t_router) * 1000)
        workflow.append(AgentStep(agent="RouterAgent", decision=decision))
        log.bind(
            level="INFO",
            agent="RouterAgent",
            conversation_id=req.conversation_id,
            user_id=req.user_id,
            execution_time_ms=router_ms,
            decision=decision,
            **{k: v for k, v in route_meta.items() if v is not None},
        ).msg("route_decision")

        t_agent = time.time()
        if decision == "MathAgent":
            try:
                agent = MathAgentLLM()
                result = agent.run(req.message)
                agent_text = result["text"]
                source_text = "MathAgent (LLM+AST)"
                summary = {
                    "expr": result["meta"]["expr"],
                    "result": result["meta"]["result"],
                    "llm_ms": result["meta"]["llm_latency_ms"],
                }
            except MathError as e:
                agent_text = f"Couldn't compute: {e}"
                source_text = "MathAgent (LLM+AST)"
                summary = {"expr": req.message, "error": str(e)}
        else:
            agent = KnowledgeAgentRedis()
            result = agent.run(req.message)
            agent_text = result["text"]
            source_text = f"Sources: {result['meta']['sources']}"
            summary = {"sources": result["meta"]["retrieved"], "llm_ms": result["meta"]["llm_ms"]}

        agent_ms = int((time.time() - t_agent) * 1000)
        workflow.append(AgentStep(agent=decision))

        log.bind(
            level="INFO",
            agent=decision,
            conversation_id=req.conversation_id,
            user_id=req.user_id,
            execution_time_ms=agent_ms,
            summary=summary,
        ).msg("agent_execution_ok")

        try:
            r.rpush(f"conversation:{req.conversation_id}", json.dumps({
                "role": "user", "content": req.message, "user_id": req.user_id
            }))
            r.rpush(f"conversation:{req.conversation_id}", json.dumps({
                "role": "assistant", "content": agent_text, "agent": decision
            }))
        except Exception as e:
            log.bind(
                level="ERROR",
                agent="Storage",
                conversation_id=req.conversation_id,
                user_id=req.user_id,
                error=str(e),
            ).msg("redis_write_failed")

        try:
            r.sadd(f"user:{req.user_id}:conversations", req.conversation_id)

            preview = (agent_text or "")[:140]
            r.hset(f"conversation_meta:{req.conversation_id}", mapping={
                "user_id": req.user_id,
                "title": f"Chat {req.conversation_id[:8]}",
                "last_message_preview": preview,
                "updated_at": str(int(time.time() * 1000)),
            })
        except Exception as e:
            log.bind(
                level="ERROR",
                agent="Storage",
                conversation_id=req.conversation_id,
                user_id=req.user_id,
                error=str(e),
            ).msg("redis_meta_failed")

        total_ms = int((time.time() - t0) * 1000)
        log.bind(
            level="INFO",
            agent="API",
            conversation_id=req.conversation_id,
            user_id=req.user_id,
            execution_time_ms=total_ms,
        ).msg("chat_request_done")

        return ChatResponse(
            response=agent_text,
            source_agent_response=source_text,
            agent_workflow=workflow,
        )
