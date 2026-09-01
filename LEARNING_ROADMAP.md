# EduPilot · 12 周学习 + 开发路线图

> 边学边做。每周 = **学什么 + 做出什么**。学不透就别往后跳。
> 默认前提：每天可投入 3-4 小时。每周实际工作量约 20-25 小时。

---

## 总览表

| 周次 | 主题 | 学到什么 | 做出什么 | 对应 JD |
|---|---|---|---|---|
| W1 | Python 补课 + LLM API 入门 | Python 工程能力、LLM API、流式输出 | 3 个 prompt 实验脚本、能跑的最小 ChatGPT 客户端 | JD 任职要求 |
| W2 | Prompt 工程 + 业务组件库雏形 | Few-shot / CoT / ReAct / 结构化输出 | `prompts/` 模板库 + `llm/` 客户端封装 | JD 2 / 4 / 加分项 |
| W3 | Web 框架（FastAPI）+ 项目骨架 | FastAPI、Pydantic、依赖注入、流式响应 | 项目骨架 + 健康检查接口 + 配置管理 | JD 任职要求 |
| W4 | RAG 基础：文档加载 + 分块 + 检索 | Embedding、向量检索、语义相似度 | 文档上传 + 检索 + 生成的最小 RAG Demo | JD 1 / 加分项 RAG |
| W5 | RAG 进阶：检索增强 + 重排序 | HyDE / Multi-Query / Rerank / 评估 | 教育讲义 RAG 模块 v1 | JD 1 |
| W6 | Agent 入门：Function Calling + ReAct | Tool Use、JSON Schema、Agent Loop | 单 Agent Demo（带 2-3 个工具） | JD 4 / 6 / 加分项 |
| W7 | 教学辅导 Agent（核心模块） | 多轮对话、个性化辅导、苏格拉底式提问 | 教学辅导 Agent v1 | JD 1 / 4 |
| W8 | 智能答疑系统（核心模块） | 意图识别、多路召回、流式生成 | 答疑接口 + 多意图分类 | JD 1 |
| W9 | AI 评测体系（JD 最特别点） | 测试集构造、指标定义、A/B 框架 | 评测模块 + 200 题数据集 + 基线对比报告 | **JD 5** |
| W10 | 多 Agent 编排（LangGraph） | 工作流、状态机、多 Agent 协作 | AI 实训工作台：讲师 Agent + 评估 Agent | JD 6 |
| W11 | LLM 业务组件库沉淀 | 可复用 Chain、提示词版本管理、错误兜底 | 组件库 v1 + 单元测试 | JD 4 |
| W12 | 整合 + 部署 + 简历包装 | Streamlit 前端、Docker、README | 可演示的 MVP + 简历文案 + 技术博客 | JD 3 / 加分项 |

**12 周后**：一个有 demo、有数据、有 README、有评测报告、能在简历讲清故事的项目。

---

## 每周详细任务

### Week 1 · LLM API 入门

**学：**
- Python 进阶：异步（asyncio）、类型注解、虚拟环境、pip 包管理
- HTTP 客户端：requests / httpx（异步）
- LLM API 基础：消息结构、temperature、max_tokens、流式响应、token 计数

**做：**
1. 在 `edu-pilot/01_intro/` 建目录
2. 写出 `hello_llm.py`：能调通 OpenAI（或兼容 API），输出回答
3. 写出 `stream_chat.py`：流式输出，体验打字机效果
4. 写出 `prompt_lab.py`：3 个不同 prompt 对比同一个问题的输出

**验收：** 能解释 `messages` 数组里 `system / user / assistant` 分别干什么；能解释 temperature 是什么。

---

### Week 2 · Prompt 工程 + 组件库雏形

**学：**
- Prompt 工程核心技巧：Few-shot、Chain-of-Thought、ReAct、Self-Consistency、Reflection
- 结构化输出：JSON Schema / Function Calling（先理论，下周实操）
- 错误处理：限流、重试、降级、超时

**做：**
1. 在 `edu-pilot/02_prompts/` 建 `prompts/` 目录，写 5 个教学场景模板：
   - 解题模板（用 CoT）
   - 出题模板（Few-shot）
   - 批改模板（评分细则嵌入）
   - 讲概念模板（苏格拉底式）
   - 学习计划模板（结构化输出）
2. 写 `components/llm_client.py`：统一的 LLM 客户端，支持 OpenAI / Anthropic / 国产模型切换
3. 写 `components/errors.py`：错误处理策略

**验收：** 5 个模板都能用同一个客户端调通，能跑批量对比实验。

---

### Week 3 · FastAPI + 项目骨架

**学：**
- FastAPI 路由、Pydantic 模型、依赖注入、中间件
- 流式返回（SSE / StreamingResponse）
- 环境变量、日志（loguru）、异常处理

**做：**
1. 在 `edu-pilot/` 建正式项目骨架（见架构文档）
2. `/health` 健康检查接口
3. `/v1/chat` 闲聊接口（还没接业务逻辑，纯打底）
4. 配置管理：用 `.env` + `pydantic-settings`

**验收：** `uvicorn` 跑起来，`curl /health` 返回 200。

---

### Week 4 · RAG 入门

**学：**
- Embedding 模型是什么（向量、相似度）
- 文档加载：PDF / Markdown / Word
- 文本分块策略：固定长度、滑动窗口、语义分块
- 向量数据库：Chroma（本地零配置）
- 检索增强生成（RAG）的端到端流程

**做：**
1. 在 `edu-pilot/04_rag_basic/` 写最小 RAG
2. 用 LangChain 加载一份 PDF 讲义 → 切块 → Embedding → 存 Chroma → 检索 → 生成
3. 跑通问答 demo，能"根据文档回答"

**验收：** 给一篇 PDF，能问出问题并答对。理解"分块策略为什么重要"。

---

### Week 5 · RAG 进阶

**学：**
- 检索优化：HyDE（假设文档）、Multi-Query（多查询改写）、Self-Query
- 重排序（Rerank）：Cross-Encoder 模型
- 元数据过滤：按章节、按难度、按来源筛选
- 简单评测：召回率、回答相关性

**做：**
1. 把 W4 的 RAG 升级
2. 加 Multi-Query 检索
3. 加 Rerank（用 sentence-transformers 本地模型，不花钱）
4. 加元数据：每个 chunk 带上章节标签
5. 写简单脚本：20 个问题测召回率

**验收：** "Python 装饰器"的回答能定位到讲义的"第 3 章函数式编程"。

---

### Week 6 · Agent 入门（Function Calling + ReAct）

**学：**
- Function Calling 协议（OpenAI / Anthropic）
- Tool Use：JSON Schema 描述工具
- ReAct 框架：Thought → Action → Observation 循环
- Agent Loop：让 LLM 决定调哪个工具、传什么参数

**做：**
1. 在 `edu-pilot/06_agent_basic/` 写第一个 Agent
2. 注册 3 个工具：
   - `search_knowledge_base(query)`：查 RAG
   - `calculator(expression)`：算数学
   - `get_current_time()`：拿当前时间
3. 让 Agent 自己决定调哪个工具

**验收：** 问"AI 实训平台 RAG 模块的检索延迟是多少？"（文档里有的）→ Agent 调工具 → 拿到答案。

---

### Week 7 · 教学辅导 Agent（核心模块）

**学：**
- 多轮对话：上下文窗口管理、历史摘要
- 个性化：根据学生画像（年级、基础、进度）调整 Prompt
- 苏格拉底式提问：不让 Agent 直接给答案，引导思考
- Memory：长期记忆（学生错题集、掌握程度）

**做：**
1. 把 W6 的 Agent 升级成"教学辅导 Agent"
2. 加学生画像：年级、目标、当前知识点
3. 加苏格拉底 Prompt：默认反问而非直接答
4. 加多轮测试：连续问 3 轮，验证上下文理解

**验收：** 模拟学生"卡住"时，Agent 能反问引导，而不是直接给答案。

---

### Week 8 · 智能答疑系统

**学：**
- 意图识别（用 LLM 分类）
- 多路召回：FAQ 库 + 文档 RAG + 计算工具
- 流式生成 + 引用展示（哪几页 / 哪几章）

**做：**
1. 设计意图分类：`概念解释` / `例题讲解` / `学习方法` / `作业批改` / `闲聊`
2. 不同意图走不同链路
3. 加引用展示

**验收：** 同样一句"我不太懂"，能区分是"概念不懂"还是"方法不懂"，走不同路径。

---

### Week 9 · AI 评测体系（JD 第 5 条）🌟

> 这是 JD 最特别、面试最爱问的能力。

**学：**
- LLM-as-Judge：用 LLM 评 LLM 输出
- 评测集构造：人工写题 + 自动生成 + 难例挖掘
- 指标体系：准确性、相关性、幻觉率、延迟、token 成本
- A/B 实验框架：同一问题两个 prompt 对比

**做：**
1. 在 `edu-pilot/09_evaluation/` 写评测框架
2. 构造数据集：
   - 50 道 Python 基础题（人工）
   - 50 道 RAG 检索题（从讲义里挖）
   - 50 道教学场景题（出题 / 批改）
   - 50 道边界 / 难例（幻觉测试）
3. 设计指标：
   - 正确率（有标准答案）
   - LLM-as-Judge 评分（无标准答案）
   - 引用准确率
   - P95 延迟
4. 跑基线：用 GPT-4o / Claude / 国内模型各跑一遍
5. 输出 `BASELINE_REPORT.md`

**验收：** 有一份能塞进简历的评测报告，**"对比 3 个模型在 200 题教学数据集上，Claude 3.5 在'概念解释'任务上 F1 高 12%"**——这种粒度。

---

### Week 10 · 多 Agent 编排（LangGraph）

**学：**
- LangGraph：节点、边、状态机
- 多 Agent 协作模式：Supervisor / Hierarchical
- 工作流：备课 → 出题 → 批改 → 反馈

**做：**
1. 引入 LangGraph
2. 3 个 Agent：
   - **讲师 Agent**：出题（用 Few-shot Prompt）
   - **学生 Agent**：模拟学生答题（故意做错）
   - **评估 Agent**：批改 + 反馈
3. 编排：让 3 个 Agent 协作完成"布置作业并批改"全流程

**验收：** 一个命令，触发"出题 → 学生答题 → 自动批改 → 出反馈"全链路。

---

### Week 11 · LLM 业务组件库沉淀

**学：**
- 组件抽象：把常用 Chain 抽出来
- 提示词版本管理（git / LangSmith）
- 单元测试 + Mock LLM

**做：**
1. `edu-pilot/components/` 下建立业务组件库：
   - `qa_chain.py`：通用问答链
   - `tutor_chain.py`：教学辅导链
   - `exam_chain.py`：出题链
   - `grading_chain.py`：批改链
   - `intent_chain.py`：意图分类链
2. 每个组件写单元测试（用 mock 不消耗 API）
3. 写 `CONTRIBUTING.md`：如何加新组件

**验收：** 新加一个业务能力，只需加一个 Chain 文件 + 注册到中心。

---

### Week 12 · 整合 + 简历包装

**学：**
- Streamlit 前端（最快搭 demo）
- Docker 化部署（加分项）
- 写技术博客 / README

**做：**
1. Streamlit 前端：4 个页面（答疑、出题、批改、评测）
2. Docker Compose 部署
3. 写 README：项目介绍、架构图、跑通步骤、效果截图
4. 写 2 篇技术博客（一篇 RAG、一篇评测）
5. 简历文案：按这个项目的亮点写
6. 录 demo 视频（3 分钟）

**验收：** 招聘方来电话："能给我看下项目吗？" → 掏出 GitHub 链接 / 录好的 demo 视频。

---

## 节奏建议

| 时段 | 干什么 | 时长 |
|---|---|---|
| 工作日晚上 | 写代码、做项目 | 2h |
| 周末上午 | 学新理论、读文档 | 2h |
| 周末下午 | 跑通新模块、补测试 | 2h |
| 周末晚上 | 写周记、调整下周计划 | 1h |

**关键纪律：**
1. **每周必须有一个可演示的产物**（截图 / 接口调用 / Demo）
2. **学不会就停**。卡 2 小时查文档 → 问 AI → 还卡就降难度
3. **学 > 写** 的时间比例前期 7:3，后期反过来

---

## 资源清单（按优先级）

| 类型 | 资源 | 用在 |
|---|---|---|
| 📚 必读 | 《LangChain 实战》、《Designing Machine Learning Systems》 | 全程 |
| 📺 视频 | Andrej Karpathy GPT 系列、3Blue1Brown DL | W1-W2 补基础 |
| 🎓 课程 | DeepLearning.AI 的 Agentic AI、LangChain 官方课 | W6-W10 |
| 🛠️ 工具 | LangChain / LlamaIndex / LangGraph 官方文档 | W4-W10 |
| 📊 评测 | LangSmith / PromptFoo / RAGAS | W9 |
| 💬 社区 | LangChain Discord、r/LocalLLaMA | 持续 |
