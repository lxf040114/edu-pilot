# W3 · FastAPI 项目骨架

> 目标：把前两周的 LLM 能力「包成一个 HTTP 服务」，让前端（W12 的 Streamlit）能调你。
> 这是 JD 里「研发 Agent 平台」最底层的「服务化」能力。

---

## 这一周你会学到什么

| 概念 | 在这周怎么体现 |
|---|---|
| **FastAPI** | 用 Python 类型注解自动生成接口文档 + 校验请求体 |
| **Pydantic** | `ChatRequest` / `Settings` 用模型约束输入，非法请求直接 422 |
| **异步 async/await** | LLM 是 IO 密集型，async 才能高并发（呼应 W1 并发实验） |
| **SSE 流式** | `/v1/chat/stream` 用 `text/event-stream` 边生成边推 |
| **配置管理** | `.env` + `pydantic-settings` 统一管理 key / model / 超时 |
| **日志** | `loguru` 记录每次请求耗时、token，方便 W9 评测埋点 |

---

## 目录结构

```
week3/
├── main.py            # FastAPI 应用：3 个接口
├── config.py          # pydantic-settings 读 .env
├── llm.py             # LLM 客户端包装（async + 流式 + .env fallback）
├── requirements.txt
├── .env.example
├── .gitignore
└── test_api.py        # 用 TestClient 离线验证 3 个接口（不用开浏览器）
```

---

## 三个接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/health` | 健康检查，返回 `{"status":"ok"}` |
| POST | `/v1/chat` | 一次性返回完整回答（JSON） |
| POST | `/v1/chat/stream` | SSE 流式返回，前端逐字显示 |

请求体：
```json
{
  "messages": [{"role": "user", "content": "什么是闭包？"}],
  "temperature": 0.7
}
```

---

## 怎么跑

```bash
cd "E:/AGI/WorkBuddy/2026-08-31-16-21-58/edu-pilot/week3"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# key 自动复用 week1/.env（llm.py 会向上找）
.venv\Scripts\python.exe test_api.py     # 离线验证 3 接口
```

想真正起服务（看 Swagger 文档）：
```bash
.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
# 浏览器开 http://127.0.0.1:8000/docs
```

---

## 原理一句话

FastAPI 收到请求 → Pydantic 校验 body → async 调 LLM → 同步接口攒完返回，流式接口用 `StreamingResponse` 把每个 token 包成 `data: {...}\n\n` 推给前端。
前端用 `EventSource` 或 `fetch` + 读流，就能实现「打字机效果」。

---

## W4 预告
W4 进入 RAG 基础：把「知识」塞进向量库（Chroma），让 /v1/chat 先检索再回答。
