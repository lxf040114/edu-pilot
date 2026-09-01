"""验证 W12 深化的两个新改动：多轮历史截断 + token 级流式接口。

用法（复用 week5 venv）：
  ..\\week5\\.venv\\Scripts\\python.exe tests\\test_stream_trim.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_trim():
    from src.agent.agent import Agent
    a = Agent(max_history=6)
    h = [{"role": "system", "content": "s"}]
    for i in range(10):
        h.append({"role": "user", "content": f"q{i}"})
        h.append({"role": "assistant", "content": f"a{i}"})
    trimmed = a._trim_history(h)
    print(f"历史截断: {len(h)} 条 → {len(trimmed)} 条")
    assert len(trimmed) <= 6 + 1  # system + 最多 max_history 条
    assert trimmed[0]["role"] == "system"
    print("✅ 历史截断正确（保留 system + 最近消息）")


def test_stream():
    from fastapi.testclient import TestClient
    from src.main import app
    client = TestClient(app)
    r = client.post("/v1/chat/stream", json={"query": "什么是闭包？"})
    body = r.text
    print(f"流式 content-type: {r.headers.get('content-type')}")
    print(f"收到 [DONE]: {'[DONE]' in body}")
    assert "text/event-stream" in r.headers.get("content-type", "")
    assert "[DONE]" in body
    print("✅ token 级流式接口正常")


if __name__ == "__main__":
    test_trim()
    test_stream()
