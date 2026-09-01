# W10 · LangGraph 多 Agent 编排

> 前几周的 Agent 都是「一个 Agent 反复调工具」。W10 换成**多 Agent 协同**：
> 讲师、学生、评估三个 Agent 各司其职，按「备课→出题→答题→批改」的流水线流转。
> 对应 JD「多步骤多工具协同自动化」。

## 一、LangGraph 四个核心概念

| 概念 | 是什么 | 本项目的例子 |
|---|---|---|
| **State** | 贯穿流程的共享状态 | `topic → question → student_answer → grade` |
| **Node** | 一个处理步骤（一个 Agent） | 讲师节点 / 学生节点 / 评估节点 |
| **Edge** | 节点间的连接，决定顺序 | 讲师→学生→评估→结束 |
| **Graph** | 节点+边组装起来，编译执行 | `builder.compile()` |

## 二、多 Agent vs 单 Agent（面试高频）

| | 单 Agent（W6/W7） | 多 Agent（W10） |
|---|---|---|
| 结构 | 一个 Agent 反复调工具 | 多个 Agent 按图流转 |
| 人设 | 一个角色 | 讲师/学生/评估各有人设 |
| 适合 | 单任务、交互式问答 | 分阶段流水线（备课→批改） |
| 状态 | 隐式（messages） | 显式 State，节点间传递 |

**本质：多智能体不是多个进程，而是多个不同人设的 LLM 调用被编排起来。**

## 三、目录结构

```
week10/
├── config.py    # 读 .env
├── llm.py       # chat（每个 Agent 大脑都用它）
├── agents.py    # ★ 三个 Agent 的大脑（出题/答题/批改）
├── graph.py     # ★ LangGraph 编排（State/Node/Edge）
├── run.py       # 运行演示
└── notes_template.md
```

## 四、怎么跑（复用 week5 venv，已装 langgraph）

```bash
cd "E:/AGI/WorkBuddy/2026-08-31-16-21-58/edu-pilot/week10"
..\week5\.venv\Scripts\python.exe run.py
```

## 五、你该懂的（面试能答）

1. LangGraph 的 State / Node / Edge 分别是什么？
2. 多 Agent 和单 Agent 的本质区别？
3. 什么场景适合多 Agent 编排（而不是单 Agent）？
4. 状态（State）为什么是「显式」的，好处是什么？

（答案在 `notes_template.md`，跑完填。）

## 六、下一步（W11）

组件库 + 整合：把前 10 周的模块（LLM 客户端/Prompt/RAG/Agent/评测）整理成统一的项目结构
`src/`，加上业务组件库，做成一个能写进简历的完整 EduPilot。最后 W12 收尾 + 简历包装。
