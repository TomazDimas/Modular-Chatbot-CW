from app.backend.agents.router_llm import RouterAgentLLM

class FakeLLM:
    def call_tool(self, **kwargs):
        return {"route": "MathAgent", "confidence": 0.92, "reason": "numbers"}

def test_router_decides_math_llm():
    agent = RouterAgentLLM(llm=FakeLLM())
    out = agent.decide("How much is 2 x 2?")
    assert out["route"] == "MathAgent"
