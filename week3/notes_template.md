# W3 学习笔记（阿布代填 · 实测数据）

> FastAPI 骨架已搭好，3 个接口用 TestClient 离线验证全过。数字来自 2026-08-31 真实运行（DeepSeek）。

---

## 实验发现

### 跑 test_api.py（实测）
| 接口 | 结果 | 关键数据 |
|---|---|---|
| GET /health | 200 | `{"status":"ok","provider":"deepseek"}` |
| POST /v1/chat | 200 | reply=闭包定义；usage=`{prompt_tokens:11, completion_tokens:38}` |
| POST /v1/chat/stream | 200 | content-type=`text/event-stream; charset=utf-8`；收到 `[DONE]` 结束标记；流式片段拼回完整回答正确 |

- loguru 打点正常：`chat done | tokens={prompt_tokens:11, completion_tokens:38} | 2.22s`
- `.env` 自动复用 week1 的 key（config.py 向上找 `../week1/.env`），无需重复填

### 三个接口各自干什么
- `/health`：探活，负载均衡/部署健康检查用，不调 LLM
- `/v1/chat`：攒完所有 token 一次性返回 JSON（适合后台批处理、评测）
- `/v1/chat/stream`：每生成一个 token 包成 `data: {...}\n\n` 推给前端（打字机效果）

---

## 概念自测（参考答法）

1. **FastAPI 为什么用类型注解就能生成文档 + 校验？** 它在运行时用 Python `typing` 反射请求体模型（Pydantic），自动生成 OpenAPI schema → `/docs` 可视化；校验失败直接返 422，不用手写 if。
2. **Pydantic 在这里管两件事？** ① 请求体 `ChatRequest`（messages/temperature 类型约束）② 配置 `Settings`（从 .env 读 key/model/timeout，带缺省值）。
3. **为什么接口用 async def？** LLM 调用是网络 IO 等待，async 下事件循环能在等待时处理别的请求，并发高（呼应 W1 并发实验：4 并发 1180ms vs 同步 4×）。
4. **SSE 流式格式为什么是 `data: ...\n\n`？** SSE 协议规定每条事件以 `data:` 开头、两个换行结束；前端 `EventSource` 按 `\n\n` 切分事件。我们每次 yield 一个 token 的 JSON。
5. **同步接口 vs 流式接口，前端体验差在哪？** 同步：用户干等直到全文生成（类似 W1 模式 A 的 2636ms）；流式：首字 747ms 就到，边出边显（W1 模式 B）。
6. **loguru 比 print 好在哪？** 自动带时间/级别/函数名/行号，一行配置切文件，方便 W9 评测时记录每次请求的 token 与耗时。

---

## 踩坑记录（本次实测）
- 原始 docstring 里 Windows 路径 `.venv\Scripts` 的反斜杠触发 `SyntaxWarning: invalid escape sequence '\S'` → 已改成正斜杠 `.venv/Scripts`，重跑无 warning。
- 其余无运行时报错。

---

## W3 自评
- [x] 搭好 FastAPI 应用，3 接口都通
- [x] Pydantic 管请求体 + 配置
- [x] async + 流式 SSE 实现打字机
- [x] .env 配置管理 + loguru 日志
- [x] 能回答上面 6 个概念问题

**打分（1-10）：** 9（骨架稳，3 接口全绿，配置/日志/异步/SSE 都覆盖）

---

## W4 预告
W4 进 RAG 基础：把「知识」塞进向量库（Chroma），让 /v1/chat 先检索再回答——从「通用聊天」变成「基于教材的助教」。
