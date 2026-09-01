# W7 · 教学辅导 Agent（整合 RAG + Agent + 教学工具）

> 这是 EduPilot 的**核心业务模块**，也是 JD「教学辅导 Agent / 智能答疑」的直接命中。
> W7 把前三周的成果拼成一个真正能「辅导学生」的 Agent。

## 一、W7 整合了什么

| 周 | 成果 | 在 W7 里的角色 |
|---|---|---|
| W2 | Prompt 模板（出题/批改/讲概念） | 变成 3 个教学工具 |
| W5 | 向量 RAG（BGE 中文嵌入） | 变成 `search_knowledge_base` 工具 |
| W6 | ReAct Agent 循环 | 串起所有工具的「大脑」 |

**一句话：Agent（决策）+ 教学工具（执行）+ RAG（教材知识）= 教学辅导 Agent。**

## 二、四个教学工具

| 工具 | 作用 | 底层 |
|---|---|---|
| `search_knowledge_base` | 向量语义检索教材 | BGE 嵌入 + Chroma（W5） |
| `generate_question` | 出题（JSON 结构化） | LLM（W2 出题模板） |
| `grade_answer` | 批改（得分/对错/评语） | LLM（W2 批改模板） |
| `explain_concept` | 讲概念（定义+类比+示例） | LLM |

对比 W6 的 `search_knowledge_base`（关键词包含匹配）→ W7 换成**向量 RAG**，
"闭包 外部变量 记住"这类口语长查询也能正确召回「闭包.md」了（语义匹配，不是字面匹配）。

## 三、目录结构

```
week7/
├── config.py          # 读 .env
├── llm.py             # chat() + chat_with_tools()
├── embedding.py       # BGEZhEmbedding（复用 W5）
├── tutoring_tools.py  # ★ 4 个教学工具 + Schema + execute
├── agent.py           # ★ ReAct 循环（复用 W6）
├── demo_tutoring.py   # 演示：覆盖 4 个工具的场景
├── knowledge_base/    # 4 篇教材（向量 RAG 检索源）
└── notes_template.md
```

## 四、怎么跑（复用 week5 的 venv）

W7 的向量 RAG 需要 torch/chroma/BGE，这些都在 week5 的 venv 里，直接复用，不用重装：

```bash
cd "E:/AGI/WorkBuddy/2026-08-31-16-21-58/edu-pilot/week7"
..\week5\.venv\Scripts\python.exe demo_tutoring.py
```

（首次跑会 ingest 教材进向量库 + 加载 BGE 模型，几秒。）

## 五、你该懂的（面试能答）

1. 教学辅导 Agent = 什么 + 什么 + 什么？
2. RAG 作为「工具」和作为「独立模块」有什么区别？（前者由 Agent 决定何时查）
3. 为什么把出题/批改做成工具而不是写死在 Agent 里？
4. W6 关键词检索 → W7 向量 RAG，解决了什么问题？

（答案在 `notes_template.md`，跑完填。）

## 六、下一步（W8）

智能答疑系统：把教学辅导 Agent 挂到 FastAPI 上，加上多轮对话记忆（历史上下文），
做成一个完整的「答疑接口」。配合 W9 评测体系，就能量化 Agent 的答疑质量了。
