from app.backend.agents.math_llm import MathAgentLLM

class FakeLLM:
    def call_tool(self, **kwargs):
        return {"expression": "2 * 2"}

def test_math_agent_simple():
    agent = MathAgentLLM(llm=FakeLLM())
    res = agent.run("How much is 2 x 2?")
    assert res["meta"]["result"] == 4
