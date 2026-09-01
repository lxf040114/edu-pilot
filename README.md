# EduPilot — 你的 AI 教育实训平台 MVP

> 对标端到端 AI 应用工程项目。每一行职责、每一项加分项，都映射到一个可演示的模块。

---

## 为什么做这个项目

岗位 JD 表面看是 7 条职责、8 条加分项，本质只有一件事：

> **用 LLM + Agent + 评测，搭建一个能解决真实业务问题的 AI 系统。**

这个项目交付一份简历拿得出手的资产 + 一套能讲清楚"我是怎么做的、能解决什么问题"的完整故事。

---

## 项目定位

| 维度 | 说明 |
|---|---|
| **业务场景** | AI 教育实训平台（MVP 版），最小可用，跑得通 |
| **核心模块** | RAG 知识库 / 教学辅导 Agent / 智能答疑 / 实训工作台 / 评测体系 |
| **使用对象** | 假设面向"参加 AI 实训的学生"和"实训讲师" |
| **可演示场景** | 学生上传讲义 → 答疑 Agent 回答 → 教学 Agent 出题 → 评测体系打分 |
| **代码量目标** | ~3000-5000 行 Python（FastAPI 后端 + Streamlit 前端 + 文档 + 测试） |
| **技术栈** | Python · FastAPI · LangChain / LlamaIndex · Chroma (本地向量库) · OpenAI/Anthropic API · Redis · Streamlit |

---

## 文档导航

| 文档 | 内容 | 谁该先读 |
|---|---|---|
| 📘 [`LEARNING_ROADMAP.md`](./LEARNING_ROADMAP.md) | 12 周学习+开发路线图，按周拆任务 | **你（第 1 件事）** |
| 🏛️ [`ARCHITECTURE.md`](./ARCHITECTURE.md) | 系统架构、模块依赖、技术选型 | **你（第 2 件事）** |
| 🔬 [`MODULE_PRINCIPLES.md`](./MODULE_PRINCIPLES.md) | 每个模块的"是什么 / 为什么 / 怎么工作" | **每个模块开发前读** |
| 🧪 [`EVALUATION.md`](./EVALUATION.md) | 评测体系（数据集、指标、A/B）—— JD 第 5 条专属 | **评测模块开发前读** |

---

## 这项目打完，简历能写什么

- ✅ "独立从 0 到 1 搭建 RAG 教育知识库（LangChain + Chroma），支持文档解析、分块策略、混合检索"
- ✅ "基于 Function Calling 设计教学辅导 Agent，支持多轮对话、工具调度、ReAct 推理"
- ✅ "搭建 LLM 评测体系：自建 200+ 题教学问答测试集，对 3 个模型做基线对比，量化指标提升 23%"
- ✅ "用 LangGraph 实现多 Agent 编排：讲师 Agent + 评估 Agent 协作，覆盖备课/出题/批改场景"
- ✅ "FastAPI 提供 8 个核心接口，Streamlit 前端可演示，覆盖 Web 全栈"

—— 这些点都是 JD 加分项的字面命中。
