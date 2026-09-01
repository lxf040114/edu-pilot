# W8 · 智能答疑系统（FastAPI + 多轮记忆）

> W7 的教学辅导 Agent 还只是「一次一问」。W8 把它做成真正的**答疑系统**：
> 挂到 FastAPI 上，加上**多轮对话记忆**，学生可以连续追问，Agent 能记住上文。

## 一、多轮记忆是怎么实现的

核心改动只有一处：Agent 的 `run()` 从「每次从零开始」变成「带上历史」。

```python
# W7：每次从零开始
def run(self, query): messages = [system, user]

# W8：带上历史
def run(self, query, history):
    messages = history + [user]   # 历史 + 新问题
    ...
    return answer, messages        # 把更新后的 messages 作为下一轮 history
```

关键：**history 就是完整的 messages 列表**（含 system、历史的 user/assistant/tool）。
每一轮把它原样传回来，模型就「记得」之前聊过什么，于是能理解「它/这个/刚才」指代谁。

## 二、接口设计

| 接口 | 作用 |
|---|---|
| `GET /health` | 健康检查（含活跃会话数） |
| `POST /v1/tutor/chat` | 答疑（非流式，带 session 记忆） |
| `POST /v1/tutor/chat/stream` | 答疑（流式 SSE） |
| `POST /v1/tutor/reset` | 清空某个会话历史 |

会话管理：`session_id → 完整 messages 历史`，存在内存 dict 里（`_sessions`）。
不同 session 互不干扰，同一 session 连续调用就是多轮对话。

## 三、目录结构

```
week8/
├── config.py          # 读 .env
├── llm.py             # chat / chat_with_tools / achat / astream
├── embedding.py       # BGEZhEmbedding（复用 W5）
├── tutoring_tools.py  # 4 教学工具（复用 W7）
├── agent.py           # ★ 多轮版 ReAct 循环（run(query, history)）
├── main.py            # ★ FastAPI 接口 + session 管理
├── test_api.py        # 验证多轮记忆 + 接口
├── demo_memory.py     # 多轮演示（不走 HTTP）
├── knowledge_base/    # 教材
└── notes_template.md
```

## 四、怎么跑（复用 week5 venv）

```bash
cd "E:/AGI/WorkBuddy/2026-08-31-16-21-58/edu-pilot/week8"

# 1. 离线验证接口 + 多轮记忆
..\week5\.venv\Scripts\python.exe test_api.py

# 2. 起服务看 Swagger
..\week5\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
# 浏览器开 http://127.0.0.1:8000/docs
```

## 五、你该懂的（面试能答）

1. 多轮记忆的本质是什么？（保存并回传 messages 历史）
2. `history` 里为什么连 tool 消息也要保存？
3. session_id 是干嘛的？（多用户隔离上下文）
4. 多轮历史会不会无限增长？怎么处理？（token 截断/摘要压缩——W9/W11 会做）

（答案在 `notes_template.md`，跑完填。）

## 六、下一步（W9）

**评测体系**（JD 单独强调的一周）：搭测试数据集 + 基线对比 + A/B 实验，量化 Agent 答疑质量——
这正是 JD 里「测试数据集 + 基线对比 + A/B 实验」的直接命中，也是面试最能讲的项目亮点。
