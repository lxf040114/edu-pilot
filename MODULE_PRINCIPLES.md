# 模块基本原理 · 每个模块的"是什么 / 为什么 / 怎么工作"

> 开发每个模块前读这一节。面试被问也能答。

---

## 模块 1：LLM 客户端封装

### 是什么

把所有 LLM API 调用统一封装到一个类，后面所有模块都通过这一个口调模型。

### 为什么

- **模型切换成本低**：今天用 GPT-4o-mini，明天换 Claude / DeepSeek，改一行
- **错误处理统一**：限流、超时、token 超长，一处兜底
- **可观测**：每次调用都记录 prompt、输出、token、延迟、cost
- **可测试**：Mock 掉，统一行为

### 怎么工作

```
Client.chat(messages) → 内部决定走哪个 Provider
                     → 统一异常处理
                     → 记录日志
                     → 返回 Response 对象
                        {
                          content: str,
                          tokens_in: int,
                          tokens_out: int,
                          latency_ms: float,
                          cost_usd: float,
                          raw: Any  # 原始响应，可选
                        }
```

### 关键 API
- `chat(messages, temperature, max_tokens)` — 普通对话
- `stream_chat(messages)` — 流式（生成器）
- `chat_with_tools(messages, tools)` — Function Calling
- `structured_output(messages, schema)` — JSON Schema 强约束输出

### 面试可能问
**Q: 为什么不用 LangChain 的 ChatModel？**
A: 屏蔽细节，便于切换和测试；LangChain 抽象更新频繁，版本兼容差。

---

## 模块 2：Prompt 模板库

### 是什么

把所有业务 Prompt 抽成模板（变量化），代码里调用而不是硬编码字符串。

### 为什么

- **可维护**：改 Prompt 不动代码
- **可评估**：同一组输入换不同 Prompt 跑评测
- **可分享**：模板集中，新人快速上手
- **可版本管理**：Git 跟踪 Prompt 演进

### 怎么工作

```python
# prompts/tutor_socratic.py
TUTOR_SOCRATIC = """你是 AI 实训平台的辅导老师。
学生画像：{student_profile}
当前章节：{chapter}
学生问题：{question}

【关键指令】不要直接给答案。先反问 1 个引导性问题让学生思考。
参考教学法：苏格拉底法、费曼学习法。

【输出格式】
- 先用 1-2 句肯定学生的思考方向
- 再抛 1 个具体的引导问题
"""
```

加载方式：
```python
from prompts import render_prompt
prompt = render_prompt("tutor_socratic", 
    student_profile={...}, 
    chapter="第3章 函数", 
    question="什么是闭包？"
)
```

### Prompt 工程核心技巧
1. **Few-shot**：给 2-3 个示例，模型照葫芦画瓢
2. **Chain-of-Thought (CoT)**：让模型 "Let's think step by step"
3. **ReAct**：Reasoning + Acting 交织（Thought → Action → Observation）
4. **Self-Consistency**：多次采样取多数答案
5. **Reflection**：让模型自我批评并修正
6. **结构化输出**：用 JSON Schema 强制格式

### 面试可能问
**Q: Few-shot 和 CoT 怎么选？**
A: 任务是"判断/分类"用 Few-shot 效率高；任务是"推理/计算"用 CoT 效果好。教学场景两者并用。

---

## 模块 3：RAG（检索增强生成）

### 是什么

让 LLM 在回答前**先检索外部知识库**，把相关内容塞进 Prompt，避免"幻觉"和"知识过时"。

### 为什么

LLM 不知道的事情：
- 公司内部文档、教材、FAQ
- 实时更新的内容
- 私有 / 垂直领域知识

RAG 是性价比最高的"给 LLM 加知识"方案（比微调便宜 100 倍）。

### 怎么工作（4 步）

```
[文档] → 切块 (Chunking) → Embedding（向量化）
                          ↓
                    存入向量数据库 (Chroma)
                          ↓
[用户提问] → Embedding → 查最相似的 top-k 块
                          ↓
              把"问题 + 检索到的块"拼成 Prompt
                          ↓
                     LLM 生成回答
```

### 关键技术点

| 环节 | 关键问题 | 常用方案 |
|---|---|---|
| 文档加载 | 各种格式 | PyMuPDF (PDF) / python-docx / markdown |
| 切块 | 块太大→噪声多，块太小→语义不全 | 句子级、滑动窗口、语义分块 |
| Embedding | 语义表达 | OpenAI text-embedding-3 / BGE |
| 检索 | 召回率 | 余弦相似度 / 混合检索（BM25 + 向量） |
| 重排序 | Top-k 里还要排最优 | Cross-Encoder（Rerank 模型） |
| 生成 | 让模型用检索内容回答 | 提示词约束"基于以下内容" |

### 进阶技巧
- **Multi-Query**：一个问题改写成 3 个角度去检索
- **HyDE**：让 LLM 先生成"假想答案"，用假想答案去检索
- **Self-Query**：让 LLM 提取元数据过滤条件
- **Rerank**：粗排 top-50 → 精排 top-5

### 面试可能问
**Q: 检索出来一堆不相关文档怎么办？**
A: 三层防御——① 改进分块（语义分块代替固定长度）；② 元数据过滤（章节 / 来源）；③ Rerank 模型精排；④ 最终 Prompt 约束。

---

## 模块 4：Function Calling & Tool Use

### 是什么

让 LLM 在回答过程中**调用外部工具**（查数据库、调 API、跑代码），把自然语言变成可执行动作。

### 为什么

LLM 本体只能"说话"，无法"做事"。Function Calling 是给它"长出手脚"——能查实时数据、能操作外部系统。

### 怎么工作（Agent Loop）

```
用户: "今天上海天气怎么样？"
     ↓
LLM 思考 → 决定调用 get_weather(city="上海")
     ↓
工具执行 → 返回 "晴，25°C"
     ↓
LLM 思考 → 信息够了，组织回答
     ↓
LLM 输出: "上海今天晴天，25°C。"
```

### 关键协议
每个工具用 JSON Schema 描述：
```json
{
  "name": "search_knowledge_base",
  "description": "从教学知识库中检索相关内容",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "检索关键词"},
      "top_k": {"type": "integer", "default": 5}
    },
    "required": ["query"]
  }
}
```

LLM 返回结构：
```json
{
  "name": "search_knowledge_base",
  "arguments": "{\"query\": \"装饰器\", \"top_k\": 3}"
}
```

代码解析 → 执行工具 → 把结果塞回 messages → 再次调 LLM → 直到 LLM 决定"我答完了"。

---

## 模块 5：Agent 框架

### 是什么

让 LLM 不只是"一次问答"，而是能**自主规划任务、自主调用工具、自主反思**的循环系统。

### 为什么

现实任务大多不是一步完成的：
- "订明天下午 3 点的会议室，邀请张三和李四" → 至少 4 步
- "查 Python 装饰器讲的最后一道例题的解析" → 检索 + 上下文 + 个性化

靠 Function Calling 一次不够，要 Agent Loop。

### 怎么工作（ReAct 模式）

```
[Loop]
1. Thought: 我需要先查 X
2. Action: tool_name(args)
3. Observation: 工具返回的结果
4. Thought: 现在我需要再查 Y
5. Action: tool_name(args)
6. Observation: ...
7. Thought: 信息够了，开始回答
[End Loop]
```

LLM 的输出格式：
```
Thought: 我需要先查课程讲义中关于"装饰器"的部分。
Action: search_knowledge_base
Action Input: {"query": "Python 装饰器 示例"}
```

### 我们的 Agent 类型

| Agent | 工具集 | 用途 |
|---|---|---|
| **教学辅导 Agent** | RAG查询 / 学生画像 / 苏格拉底反问 | 主辅导入口 |
| **答疑 Agent** | FAQ / RAG / 计算 | 简单答疑 |
| **讲师 Agent** | 出题模板 / 难度调节 | 布置作业 |
| **学生 Agent** | 答题模板 / 故意出错 | 模拟（用于多 Agent 流程） |
| **评估 Agent** | 标准答案 / 评分维度 | 批改作业 |

### 面试可能问
**Q: ReAct 和普通 Function Calling 区别？**
A: Function Calling 是协议（怎么调用工具）；ReAct 是范式（怎么推理）。ReAct 让 LLM 在每步决策前输出思考过程，更稳定可调试。

---

## 模块 6：多 Agent 编排（LangGraph）

### 是什么

让多个 Agent 协作完成复杂工作流。用 LangGraph 的状态机表达。

### 为什么

单个 Agent 处理"出题 + 批改 + 反馈"全流程，容易飘。
拆成多个专门的 Agent 协作：
- 讲师 Agent：负责出题
- 评估 Agent：负责批改
- 主管 Agent：负责协调

### 怎么工作（状态机）

```
                ┌─────────┐
                │  Start  │
                └────┬────┘
                     ↓
            ┌─────────────────┐
            │  Lecturer Agent │ → 出题
            └────────┬────────┘
                     ↓
            ┌─────────────────┐
            │  Student Agent  │ → 模拟答题
            └────────┬────────┘
                     ↓
            ┌─────────────────┐
            │ Evaluator Agent │ → 批改
            └────────┬────────┘
                     ↓
                ┌─────────┐
                │   End   │
                └─────────┘
```

每个节点是个函数，节点之间是边。LangGraph 自动管理状态。

### 进阶模式
- **Supervisor**：加一个"主管"Agent，决定下一步给谁
- **Hierarchical**：Agent 嵌套 Agent
- **Cyclic**：支持循环（批改不通过 → 让学生重做）

### 面试可能问
**Q: 为什么不直接用一个 Agent 干到底？**
A: 1）责任清晰，每个 Agent 只擅长一件事；2）可单测；3）替换其中某个 Agent 不影响整体；4）解决"上下文窗口爆炸"问题。

---

## 模块 7：AI 评测体系

### 是什么

用**可量化的指标**评估 LLM 应用效果，是 LLM 上线前必经环节。

### 为什么

- 不能凭感觉："我觉得这版 Prompt 更好"不算数
- 不量化就优化不了：不知道改哪个
- 老板/客户问"效果怎么样？"得有数据说话

### 评测三层

#### 第 1 层：基础指标（机器可算）
| 指标 | 定义 |
|---|---|
| 延迟 P95 | 95% 请求响应时间 |
| Token 数 | 平均输入/输出 token |
| 成功率 | 200 OK 占比 |
| Cost | 每次调用费用 |

#### 第 2 层：质量指标（有/无标准答案）
| 指标 | 用法 |
|---|---|
| 准确率 | 答案 = 标准答案（选择题） |
| F1 / EM | 抽取式问答（与标准文本匹配度） |
| 召回率 | RAG 检索（相关文档是否召回了） |
| 引用准确率 | 引用页码是否正确 |

#### 第 3 层：LLM-as-Judge（无标准答案）
- 用 GPT-4 做"裁判"，按维度评分（1-5）
- 维度：相关性、准确性、流畅度、教学价值
- ⚠️ LLM 评 LLM 有偏，但大规模评测够用

### 怎么跑 A/B 实验

```
对照组: prompt_v1 + model_gpt4o
实验组: prompt_v2 + model_claude

对 200 题各跑一遍 → 计算指标 → 输出报告

报告示例：
┌────────────────┬──────────┬─────────┬──────────┐
│ 维度           │ v1+GPT4o │ v2+Claude│ 提升    │
├────────────────┼──────────┼─────────┼──────────┤
│ 概念解释 F1    │ 0.72     │ 0.81    │ +12.5%  │
│ 出题可用率     │ 78%      │ 86%     │ +10.3%  │
│ P95 延迟       │ 1200ms   │ 950ms   │ -20.8%  │
│ 平均 token 成本│ $0.012   │ $0.018  │ +50%    │
└────────────────┴──────────┴─────────┴──────────┘

结论：v2+Claude 质量更好，成本更高。
```

### 面试可能问
**Q: LLM-as-Judge 也有错怎么办？**
A: 三招：① 多个裁判投票；② 用人类标注 100 题做校准（看裁判分数和人评分的相关系数）；③ 关键场景必须人评。

---

## 模块 8：FastAPI 后端

### 是什么

Python 的现代异步 Web 框架，给前端提供 RESTful API。

### 为什么

- LLM 应用全是 IO 密集（等 API 返回），FastAPI 的 async 完美匹配
- 自动 OpenAPI 文档（前端能直接对接）
- Pydantic 自动校验请求参数

### 关键模式

#### 流式响应（SSE）
```python
from fastapi.responses import StreamingResponse

@app.post("/v1/chat/stream")
async def stream_chat(req: ChatRequest):
    async def event_generator():
        async for chunk in llm.stream_chat(req.messages):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

前端用 `EventSource` 或 `fetch` 接收，体验"打字机"效果。

---

## 模块 9：向量数据库（Chroma）

### 是什么

专门存"向量"（一组浮点数）的数据库。向量 = 文本的语义编码。

### 为什么

- 传统数据库查的是精确匹配（`WHERE content LIKE '%装饰器%'`），不懂语义
- 向量数据库查的是"最相似"（"装饰器"和"函数包装"很相近，传统 DB 觉得没关系）
- RAG 的核心检索层

### 怎么工作

```python
import chromadb

# 1. 客户端
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("lectures")

# 2. 写入
collection.add(
    ids=["doc1_chunk1", "doc1_chunk2"],
    documents=["装饰器是 Python 的特性...", "它接受函数..."],
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    metadatas=[{"chapter": "3"}, {"chapter": "3"}]
)

# 3. 检索
results = collection.query(
    query_embeddings=[[0.15, 0.25, ...]],  # 用户问题的向量
    n_results=5
)
# → 返回 top-5 最相似的 chunks
```

### 对比

| 向量库 | 部署 | 适用 |
|---|---|---|
| Chroma | 本地文件 | 小项目、个人项目 ✅ |
| Milvus | 独立服务 | 中大规模 |
| Pinecone | 云服务 | 不想运维 |
| Weaviate | 自部署 | 复杂过滤 |

教学场景下，Chroma 够用。

---

## 模块 10：Vibe Coding（Cursor / Claude Code）

### 是什么

用 AI 写代码——不是替代思考，而是把"敲键盘"换成"审核 + 调整"。

### 为什么

JD 写了"常态化使用 Cursor / Claude Code / Devin / Copilot"，这是新型开发模式，必须会。

### 怎么工作（核心工作流）

1. **需求拆解**：把任务写成结构化 Prompt（模块名 / 期望行为 / 接口）
2. **上下文准备**：把相关文件喂给 AI（@file、附代码片段）
3. **生成**：AI 出第一版代码
4. **审视**：人工看（命名、逻辑、边界）
5. **迭代**：不满意 → 提反馈 → 再生成
6. **测试**：写测试 → 跑通 → 改 AI 代码

### 关键心法

- **Prompt 质量 = 代码质量**
- **小步快跑**：一次只让 AI 改 50 行，别让它重写整个模块
- **永远 review**：AI 90% 的输出能用，但 10% 是毒
- **上下文聚焦**：别塞无关文件，AI 会分心

### 实战场景示例

| 场景 | Vibe Coding 怎么用 |
|---|---|
| 写新模块 | 给 AI 模块名 + 接口签名 + 期望行为，让它先生成骨架 |
| 改 bug | 给 AI 报错信息 + 怀疑的几行代码，让它分析 + 修 |
| 写测试 | 给 AI 函数签名，让它生成 pytest 测试用例 |
| 重构 | 选中一块代码，`/refactor` 让 AI 提方案 |
| 写文档 | 让 AI 读代码生成 docstring |

---

## 总结：每个模块对应的"能讲清的事"

| 模块 | 能讲清 |
|---|---|
| LLM 客户端 | 怎么统一抽象、为什么不用 LangChain |
| Prompt 库 | 几大工程技巧、什么时候用什么 |
| RAG | 端到端流程、检索优化方向 |
| Function Calling | 协议规范、Agent Loop |
| Agent | ReAct 模式、我们这有哪几种 Agent |
| 多 Agent | 状态机、为什么拆 Agent |
| 评测 | 三层指标体系、A/B 框架 |
| FastAPI | 异步 + 流式 |
| 向量库 | 向量化语义检索原理 |
| Vibe Coding | 工作流、心法 |

这 10 个讲清，面试稳了。
