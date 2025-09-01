def test_chat_math_e2e(monkeypatch, client):
    from app.backend.agents.router_llm import RouterAgentLLM
    def fake_decide(self, msg): return {"route": "MathAgent"}
    monkeypatch.setattr(RouterAgentLLM, "decide", fake_decide)

    resp = client.post("/chat", json={"message":"2 + 2","user_id":"u1","conversation_id":"c1"}).json()
    assert resp["agent_workflow"][0]["decision"] == "MathAgent"
    assert "response" in resp
