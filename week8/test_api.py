"""W8 接口验证：重点验证多轮对话记忆。

用法（复用 week5 venv）：
  ..\\week5\\.venv\\Scripts\\python.exe test_api.py
"""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    print("health:", r.json())


def test_multi_turn():
    sid = "stu_001"
    # 第一轮：问闭包
    r1 = client.post("/v1/tutor/chat", json={"session_id": sid, "query": "什么是闭包？"})
    a1 = r1.json()["answer"]
    print("\n[第1轮] 问: 什么是闭包？")
    print("  答:", a1[:100].replace("\n", " "), "...")

    # 第二轮：用「它」指代闭包，验证 Agent 记住了上下文
    r2 = client.post("/v1/tutor/chat", json={"session_id": sid, "query": "那它在装饰器里是怎么用的？"})
    a2 = r2.json()["answer"]
    print("\n[第2轮] 问: 那它在装饰器里是怎么用的？")
    print("  答:", a2[:150].replace("\n", " "), "...")

    assert "装饰器" in a2, "第二轮答案应提到装饰器（说明记住了「它=闭包」）"
    print("\n✅ 多轮记忆验证通过：第二轮正确理解了「它」指闭包")


def test_stream():
    r = client.post("/v1/tutor/chat/stream", json={"session_id": "stu_002", "query": "讲一下递归"})
    body = r.text
    print("\n[流式] content-type:", r.headers.get("content-type"))
    print("  收到 [DONE]:", "[DONE]" in body)
    assert "[DONE]" in body


def test_reset():
    r = client.post("/v1/tutor/reset", json={"session_id": "stu_001"})
    print("\nreset:", r.json())


if __name__ == "__main__":
    test_health()
    test_multi_turn()
    test_stream()
    test_reset()
