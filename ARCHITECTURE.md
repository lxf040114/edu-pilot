# EduPilot · 架构设计

## 总览

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit 前端 (W12)                       │
│   答疑 │ 出题 │ 批改 │ 评测                                   │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP / SSE
┌────────────────────────────▼────────────────────────────────┐
│                    FastAPI 后端 (W3)                         │
│   /chat │ /tutor │ /qa │ /exam │ /evaluate │ /workbench    │
└──┬───────────┬───────────┬───────────┬───────────┬──────────┘
   │           │           │           │           │
┌──▼──┐  ┌────▼────┐  ┌────▼────┐  ┌────▼────┐  ┌──▼──────┐
│ LLM │  │   RAG   │  │  Agent  │  │ 多Agent │  │  评测   │
│ 组件│  │  知识库 │  │  教学   │  │ 编排    │  │  体系   │
│     │  │         │  │  答疑   │  │ LangGraph│ │         │
└──┬──┘  └────┬────┘  └────┬────┘  └────┬────┘  └──┬──────┘
   │         │             │            │          │
   └─────────┴─────────────┴────────────┴──────────┘
                             │
                    ┌────────▼─────────┐
                    │  基础组件层        │
                    │  客户端/日志/配置  │
                    │  向量库 Chroma    │
                    │  Redis (会话/缓存)│
                    └──────────────────┘
```

---

## 目录结构

```
edu-pilot/
├── README.md                       # 项目总览（本仓的入口）
├── LEARNING_ROADMAP.md             # 12 周学习+开发路线
├── ARCHITECTURE.md                 # 本文件
├── MODULE_PRINCIPLES.md            # 每个模块基本原理
├── EVALUATION.md                   # 评测体系设计
│
├── weekN/                          # 按周迭代的工作目录
│   ├── 01_intro/
│   ├── 02_prompts/
│   ├── 03_fastapi/
│   ├── 04_rag_basic/
│   ├── ...
│   └── 12_polish/
│
├── src/                            # 项目主体代码（W12 整合后迁移）
│   ├── api/                        # FastAPI 路由
│   │   ├── chat.py
│   │   ├── tutor.py
│   │   ├── qa.py
│   │   ├── exam.py
│   │   ├── evaluate.py
│   │   └── workbench.py
│   │
│   ├── components/                 # 业务组件库
│   │   ├── llm_client.py
│   │   ├── prompts/
│   │   ├── chains/
│   │   ├── tools/
│   │   └── errors.py
│   │
│   ├── modules/                    # 核心业务模块
│   │   ├── rag/                    # RAG 知识库
│   │   │   ├── loader.py
│   │   │   ├── splitter.py
│   │   │   ├── retriever.py
│   │   │   └── reranker.py
│   │   │
│   │   ├── agent/                  # Agent 框架
│   │   │   ├── base.py
│   │   │   ├── tutor_agent.py      # 教学辅导
│   │   │   ├── qa_agent.py         # 答疑
│   │   │   └── tools_registry.py
│   │   │
│   │   ├── orchestrator/           # 多 Agent 编排
│   │   │   ├── langgraph_flow.py
│   │   │   ├── lecturer_agent.py
│   │   │   ├── student_agent.py
│   │   │   └── evaluator_agent.py
│   │   │
│   │   └── evaluation/             # 评测
│   │       ├── dataset.py
│   │       ├── metrics.py
│   │       ├── runner.py
│   │       └── reporter.py
│   │
│   ├── infra/                      # 基础设施
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── db.py                   # Chroma 客户端
│   │   └── redis_client.py
│   │
│   └── main.py                     # FastAPI 入口
│
├── tests/                          # 单元测试
├── data/                           # 教学讲义 / FAQ / 测试集
│   ├── lectures/                   # 上传的讲义
│   ├── faq/
│   └── evaluation/
│       ├── python_basics.jsonl
│       ├── rag_retrieval.jsonl
│       └── tutor_scenarios.jsonl
│
├── reports/                        # 评测报告输出
│   └── baseline_2026q1.md
│
├── docker/                         # 容器化
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── frontend/                       # Streamlit
│   └── app.py
│
└── scripts/                        # 工具脚本
    ├── ingest_lectures.py          # 批量导入讲义
    ├── run_evaluation.py           # 跑评测
    └── seed_data.py
```

---

## 模块依赖关系

```
Week 1: LLM API 基础（独立）
   ↓
Week 2: Prompt 组件库 + LLM 客户端封装（独立）
   ↓
Week 3: FastAPI 骨架（依赖 W2 的客户端）
   ↓
Week 4: RAG 基础（依赖 W1+W3，demo 形式）
   ↓
Week 5: RAG 进阶（依赖 W4）
   ↓
Week 6: Agent 基础（依赖 W1）
   ↓
Week 7: 教学辅导 Agent = W6 升级（依赖 W5 RAG）
   ↓
Week 8: 答疑系统 = W7 升级 + 意图识别（依赖 W7）
   ↓
Week 9: 评测体系（独立，可并行）
   ↓
Week 10: 多 Agent 编排（依赖 W7+W8 + LangGraph）
   ↓
Week 11: 业务组件库（依赖前面所有）
   ↓
Week 12: 前端 / Docker / 整合（依赖前面所有）
```

---

## 技术选型说明

| 组件 | 选型 | 理由 | 备选 |
|---|---|---|---|
| LLM API | OpenAI GPT-4o / Anthropic Claude 3.5 | 主流能力强、文档全 | 通义千问 / DeepSeek（成本低） |
| LLM 客户端 | 统一封装（自写） | 一处切换多个模型 | LangChain 的 ChatModel（封装重） |
| Web 框架 | FastAPI | 异步原生、文档自动生成、性能好 | Flask（同步老旧） / Django（重） |
| RAG 框架 | LangChain 0.2+ | 社区大、文档全、生态丰富 | LlamaIndex（数据处理更好） |
| 向量数据库 | Chroma | 本地零配置、Python 原生 | Milvus（重）/ Pinecone（云） |
| Embedding | text-embedding-3-small | OpenAI 性价比最优 | BGE / M3E（本地） |
| 重排序 | bge-reranker-base（本地） | 免费、不消耗 API | Cohere Rerank（云） |
| Agent 框架 | 原生 Function Calling + ReAct | 学底层原理 | LangChain Agent（封装重） |
| 多 Agent | LangGraph | 状态机灵活、表达力强 | AutoGen / CrewAI |
| 评测 | 自研 + RAGAS 借鉴 | 教学场景特殊 | LangSmith / PromptFoo（云） |
| 前端 | Streamlit | 最快出 demo | React（重）/ Gradio |
| 缓存/会话 | Redis | 标配 | 内存（轻） |
| 部署 | Docker Compose | 简单 | K8s（重） |

---

## 关键设计决策

### 决策 1：先用 OpenAI 还是国产模型？

**先用 OpenAI（GPT-4o-mini 起步）**，原因：
- 文档质量最好、社区答案最多
- 价格便宜（mini 0.15/1M tokens），够学完 12 周
- 等熟悉了再切国产模型（兼容接口，改个 base_url 就行）

### 决策 2：Embedding 用 OpenAI 还是本地？

**优先 OpenAI（text-embedding-3-small）**，文档少时不卡，本地模型速度慢。
后期如果跑大量数据，再切 BGE 本地。

### 决策 3：每个模块独立目录 vs 统一 src/？

**前期按周目录分**（week1/ week2/），方便不同时期文件不冲突。
**W12 整合时迁移到 `src/`**，按模块分目录。

### 决策 4：用 LangChain 还是自己写？

**关键模块自己写**（RAG、Agent Loop），LangChain 只用作辅助工具。
原因：面试会问"为什么要这样设计"，自己写过能答；只调 API 不会。

### 决策 5：评测数据从哪来？

- 50% 人工写（从讲义里筛核心点）
- 30% LLM 生成 + 人工校对
- 20% 真实学生提问 logs（如果没有可公开数据集，如 SCROLLS、HotpotQA）

---

## 数据流图

### 答疑场景
```
学生提问 → FastAPI /qa
       → 意图识别 (LLM)
       → 路由到 RAG / 工具 / 直接答
       → 检索 Chroma → 取 top-k → 重排序
       → LLM 生成（含引用）
       → 流式返回 → 前端展示
```

### 教学辅导场景
```
学生提问 → FastAPI /tutor
        → 加载学生画像
        → 教学 Agent 进入 Loop：
            - 思考（Thought）
            - 决定调哪个工具（Action）：
                a) search_kb → 查 RAG
                b) get_history → 学生错题集
                c) ask_socratic → 反问引导
            - 拿到结果（Observation）
            - 再思考
        - 直到决定结束
        → 输出回答
```

### 评测场景
```
评测集 (jsonl) → 评测 Runner
              → 对每个 case 调用候选模型
              → 收集输出 + 指标（延迟/token）
              → LLM-as-Judge 打分
              → 输出报告 (md + json)
              → 可对比多模型 / 多 prompt 版本
```

---

## 不在本期目标内（避免 scope creep）

- ❌ 用户系统、登录、付费（用 mock 数据）
- ❌ 真实讲义版权（用公开样例、合成数据）
- ❌ 多模态（语音、图像）—— JD 提了但不是必须
- ❌ 微调模型 —— JD 提了但优先级低
- ❌ 多语言 i18n
- ❌ K8s 部署
