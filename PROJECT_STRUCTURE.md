# EduPilot · 正式项目结构（W11 整合）

> 前 10 周按 `weekN/` 迭代，W11 归拢成正式 `src/` 结构——这是能直接写进简历、让面试官一眼看懂的项目形态。

## 一、目录结构

```
edu-pilot/
├── src/                      # 核心代码（正式结构）
│   ├── core/                 # 基础设施
│   │   ├── config.py         #   配置（pydantic-settings，支持国产模型）
│   │   └── llm.py            #   LLM 客户端（同步/异步/流式/带工具）
│   ├── rag/                  # RAG 层
│   │   ├── embedding.py      #   BGE-zh 中文嵌入
│   │   └── retriever.py      #   Chroma 向量检索
│   ├── agent/                # Agent 层
│   │   ├── tools.py          #   教学工具（出题/批改/讲概念/检索）
│   │   └── agent.py          #   ReAct 循环（多轮记忆）
│   ├── prompts/              # Prompt 层
│   │   └── teaching.py       #   5 个教学模板
│   ├── graph/                # 编排层
│   │   └── orchestration.py  #   LangGraph 多 Agent（讲师/学生/评估）
│   ├── eval/                 # 评测层
│   │   ├── metrics.py        #   指标（关键词命中 + LLM 评委）
│   │   └── evaluator.py      #   A/B 实验流程
│   └── main.py               # FastAPI 统一入口
├── data/
│   ├── knowledge_base/       # 教材（4 篇）
│   └── eval_data.json        # 评测集（8 题）
├── tests/
│   └── test_smoke.py         # 冒烟测试
├── week1/ ~ week10/          # 迭代历史（学习路径，可回看）
└── README.md / LEARNING_ROADMAP.md / ARCHITECTURE.md / MODULE_PRINCIPLES.md
```

## 二、模块 ↔ JD 职责对照

| 模块 | 对应 JD |
|---|---|
| `src/rag/` | RAG 知识库 |
| `src/agent/` | 教学辅导 Agent + 智能答疑 + 工具调用链路 |
| `src/prompts/` | Prompt 工程 |
| `src/graph/` | 多智能体编排（多步骤多工具协同） |
| `src/eval/` | 测试数据集 + 基线对比 + A/B 实验 |
| `src/core/` | 配置管理 + LLM 接入 |

## 三、简历能写的亮点

- 基于 **FastAPI + LangChain/LangGraph + Chroma** 搭建 AI 教育实训平台 EduPilot，8 个核心模块
- **RAG**：BGE-zh 中文嵌入 + 向量检索，替换英文 MiniLM 后检索 top1 命中率 2/4 → 4/4
- **Agent**：Function Calling + ReAct 循环，实现教学辅导 Agent（出题/批改/讲概念多工具协同）
- **多 Agent 编排**：LangGraph 编排讲师/学生/评估三 Agent，覆盖备课→出题→批改全流程
- **评测体系**：8 题测试集 + LLM-as-judge，A/B 对比无 RAG vs 有 RAG，量化定位检索缺陷
- **多轮对话**：session 级对话记忆，支持上下文指代理解

## 四、怎么跑

```bash
cd "E:/AGI/WorkBuddy/2026-08-31-16-21-58/edu-pilot"

# 冒烟测试（验证整合后各模块正常）
week5\.venv\Scripts\python.exe tests\test_smoke.py

# 起服务
week5\.venv\Scripts\python.exe -m uvicorn src.main:app --reload --port 8000
# 文档：http://127.0.0.1:8000/docs
```
