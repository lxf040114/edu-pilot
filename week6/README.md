# W6 · Agent 入门：Function Calling 循环（ReAct）

> W2 你见过 Function Calling 的「单次调用」demo（模型调一次 calculator 就得答案）。
> W6 把它升级成真正的 **Agent 循环**：模型可以**自己决定调哪个工具、调几次、按什么顺序**。

## 一、ReAct 循环是什么

ReAct = **Reasoning（推理）+ Acting（行动）** 交替进行：

```
用户提问
   ↓
[推理] 模型决定：该调什么工具？传什么参数？  → 返回 tool_calls
   ↓
[行动] 你的代码执行工具，拿到结果
   ↓
把结果作为 tool 消息回传给模型
   ↓
[再推理] 模型结合结果：继续调下一个工具？还是给最终答案？
   ↓
（循环，直到模型不再调工具 → 输出最终答案）
```

关键：**Agent = 大模型 + 工具 + 这个循环**。大模型只负责「决策」，工具负责「干活」，循环把两者串起来。

## 二、工具注册（tools.py）

每个工具要两样东西：
1. **JSON Schema**（给模型看）：`name` / `description` / `parameters`，模型靠这个理解「什么时候该调、参数长什么样」
2. **Python 函数**（给代码执行）：真正干活的逻辑

W6 提供 3 个演示工具：
| 工具 | 作用 |
|---|---|
| `calculator` | AST 白名单安全计算（不直接 eval，防注入） |
| `get_current_time` | 当前时间 |
| `search_knowledge_base` | 关键词检索教材（W6 简化版，W7 换向量 RAG） |

## 三、W2 → W6 的跃迁

| | W2（demo_function_calling） | W6（agent.py） |
|---|---|---|
| 调用次数 | 1 次（写死：调 calculator） | 循环（模型自主决定） |
| 工具 | 1 个硬编码 | 3 个，注册表统一管理 |
| 多步协同 | 不支持 | 支持（一次问题用多个工具） |
| 出错处理 | 无 | execute 捕获异常回传 |

## 四、目录结构

```
week6/
├── config.py       # 读 .env（向上复用 week1 的 key）
├── llm.py          # chat() + chat_with_tools()（带 tools 参数）
├── tools.py        # 工具 Schema + 实现 + execute 分发
├── agent.py        # ★ ReAct 循环（核心）
├── demo_agent.py   # 演示：含一次「多工具协同」
├── knowledge_base/ # 4 篇教材（search_knowledge_base 用）
└── notes_template.md
```

## 五、怎么跑

```bash
cd "E:/AGI/WorkBuddy/2026-08-31-16-21-58/edu-pilot/week6"
python -m venv .venv
.venv\Scripts\activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
.venv\Scripts\python.exe demo_agent.py
```

## 六、你该懂的（面试能答）

1. Agent 的本质 = 什么 + 什么 + 什么？
2. ReAct 的「推理」和「行动」各指哪一步？
3. 工具为什么要有 JSON Schema，而不是直接给函数？
4. 为什么 assistant 消息的 tool_calls 要原样回传？
5. 循环为什么要设最大轮次？

（答案在 `notes_template.md`，跑完填。）

## 七、下一步（W7）

教学辅导 Agent：把 Agent 循环套到真实业务上——加「出题 / 批改 / 讲概念」教学工具，
配合 W5 的向量 RAG，做成一个真正能「辅导学生」的 Agent。这是 EduPilot 的核心业务模块。
