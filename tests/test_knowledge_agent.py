from app.backend.agents.knowledge_redis import KnowledgeAgentRedis

class FakeLLM:
    def generate(self, system: str, user: str) -> str:
        return "InfiniteTap allows tap-to-pay with your phone."

def fake_knn_search(r, qvec, k):
    return [
        {"source": "https://ajuda.infinitepay.io/...", "text": "InfiniteTap is ...", "score": 0.98}
    ]

def test_knowledge_agent_offline(monkeypatch):
    from app.backend.agents import knowledge_redis
    monkeypatch.setattr(knowledge_redis, "_knn_search", fake_knn_search)
    agent = KnowledgeAgentRedis(llm=FakeLLM())
    res = agent.run("O que é o InfiniteTap?")
    assert "InfiniteTap" in res["text"]
    assert "sources" in res["meta"]
