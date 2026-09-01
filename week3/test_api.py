"""离线验证 3 个接口（不用开浏览器 / 不用起 uvicorn 服务）。

用 FastAPI 自带的 TestClient 在进程内发请求，验证路由 + 流式格式都正常。
跑：.venv/Scripts/python.exe test_api.py
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("=" * 60)
print("1) GET /health")
r = client.get("/health")
print("   ", r.status_code, r.json())

print("=" * 60)
print("2) POST /v1/chat（一次性）")
body = {"messages": [{"role": "user", "content": "用一句话解释什么是闭包？"}], "temperature": 0.7}
r = client.post("/v1/chat", json=body)
print("   ", r.status_code)
print("   reply:", r.json()["reply"])
print("   usage:", r.json()["usage"])

print("=" * 60)
print("3) POST /v1/chat/stream（SSE 流式）")
with client.stream("POST", "/v1/chat/stream", json=body) as resp:
    print("   status:", resp.status_code, "content-type:", resp.headers.get("content-type"))
    collected = []
    for line in resp.iter_lines():
        if not line:
            continue
        if line.startswith("data: "):
            payload = line[len("data: "):]
            if payload == "[DONE]":
                print("   [DONE] 收到结束标记")
                break
            delta = __import__("json").loads(payload)["delta"]
            collected.append(delta)
    print("   流式拼回完整回答：", "".join(collected))

print("=" * 60)
print("✅ 3 个接口全部验证通过")
