"""离线验证 /v1/rag 接口（用 TestClient，不用起服务）。

跑：.venv/Scripts/python.exe test_api.py
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("=" * 60)
print("POST /v1/rag（先检索教材再回答）")
body = {"query": "装饰器和闭包有什么关系？", "top_k": 5, "temperature": 0.3}
r = client.post("/v1/rag", json=body)
print("   status:", r.status_code)
data = r.json()
print("   回答：", data["answer"])
print("   召回片段数：", len(data["retrieved"]))
for i, c in enumerate(data["retrieved"][:3]):
    print(f"     #{i+1} 来源={c['source']} 距离={c['distance']}")
print("   usage：", data["usage"])

print("=" * 60)
print("✅ /v1/rag 接口验证通过")
