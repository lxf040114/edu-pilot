# W2 · Prompt 组件库 + Function Calling 封装

> W1 你学会了"调通 LLM"。W2 解决一个实际问题：**Prompt 散落在代码里 = 灾难**。
> 这一周把教学场景的 Prompt 抽成"模板库"，并给客户端加上 Function Calling 能力（为 W6 的 Agent 铺路）。

---

## 1. 为什么要抽 Prompt 模板（30 分钟）

W1 里 Prompt 是写死在 `hello_llm.py` 里的字符串。项目一大就会炸：

| 问题 | 抽模板后 |
|---|---|
| 改一句提示词要翻代码 | 模板集中，一处改 |
| 不知道哪个 Prompt 效果更好 | 同一输入换模板跑评测（W9 用） |
| 新人接手看不懂 | 模板带注释，自解释 |
| Prompt 演进没法追溯 | Git 跟踪 `.py` 文件变更 |
| 多个模块重复同一段 system | 复用同一个模板函数 |

**核心思想**：Prompt 也是代码，要模块化、可测试、可版本化。

---

## 2. 五个教学场景模板

我们 EduPilot 是 AI 教育实训平台，抽 5 个最通用的教学 Prompt：

| 模板 | 场景 | 用的技巧 |
|---|---|---|
| `solve_problem` | 给学生解题 | **CoT**（一步步推理） |
| `generate_question` | 老师出题 | **Few-shot**（给示例定格式） |
| `grade_answer` | 批改作业 | 评分细则 + **结构化输出** |
| `explain_concept` | 讲概念 | **苏格拉底式**（反问引导） |
| `plan_study` | 生成学习计划 | **结构化输出**（JSON） |

每个模板都是一个 Python 函数，返回 `messages` 列表，主程序直接喂给 `client.chat()`。

### 2.1 solve_problem（解题 · CoT）

```python
def solve_problem_prompt(question, student_level="初学者"):
    system = (
        "你是 Python 辅导老师。解题必须：\n"
        "1. 先判断学生卡在哪\n"
        "2. 一步步写出推理（Chain-of-Thought）\n"
        "3. 最后给可运行代码 + 解释\n"
        f"学生水平：{student_level}。用他能懂的比喻。"
    )
    user = f"题目：{question}\n\n请一步步解答。"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
```

**为什么 CoT**：数学/编程题不让模型"直接给答案"很容易算错或跳步。强制 step-by-step 准确率显著上升。

### 2.2 generate_question（出题 · Few-shot）

```python
def generate_question_prompt(topic, difficulty="简单", n=3):
    system = "你是出题老师，严格按照示例格式输出。"
    few_shot = [
        {"role": "user", "content": "给『列表』出 1 道简单题"},
        {"role": "assistant", "content":
         "【题目】如何用列表存 5 个学生的成绩并求平均分？\n"
         "【考点】列表遍历、sum()、len()\n"
         "【难度】简单"},
    ]
    user = f"给『{topic}』出 {n} 道{difficulty}题，沿用上面格式。"
    return [{"role": "system", "content": system}, *few_shot,
            {"role": "user", "content": user}]
```

**为什么 Few-shot**：让模型照葫芦画瓢，输出格式 100% 稳定（评测时能机器解析）。

### 2.3 grade_answer（批改 · 结构化输出）

```python
def grade_answer_prompt(question, student_answer, reference):
    system = (
        "你是批改老师。按维度打分并给改进建议。\n"
        "必须严格输出 JSON：\n"
        '{"score": <0-100>, "correct": <true/false>, '
        '"missing": ["漏掉的点"], "advice": "改进建议"}'
    )
    user = f"题目：{question}\n学生答案：{student_answer}\n标准答案：{reference}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
```

**为什么结构化输出**：批改结果要存数据库、要算班级平均分——必须机器能解析，不能是一段散文。

### 2.4 explain_concept（讲概念 · 苏格拉底式）

```python
def explain_concept_prompt(concept, student_level="初学者"):
    system = (
        "你是苏格拉底式老师。规则：\n"
        "1. 绝不直接给定义\n"
        "2. 先用 1 句肯定学生的好奇心\n"
        "3. 抛 1 个引导性问题让他自己想\n"
        "4. 等他回答后再递进"
        f"学生水平：{student_level}"
    )
    user = f"什么是『{concept}』？"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
```

**为什么苏格拉底式**：JD 要"教学辅导 Agent"——好的辅导不是喂答案，是引导思考。这是 EduPilot 的教学法内核。

### 2.5 plan_study（学习计划 · 结构化输出）

```python
def plan_study_prompt(goal, weeks, current_level="零基础"):
    system = (
        "你是学习规划师。输出严格 JSON：\n"
        '{"week1": "...", "week2": "...", ..., "milestone": "结业标准"}'
    )
    user = f"目标：{goal}\n周期：{weeks} 周\n当前水平：{current_level}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
```

---

## 3. Function Calling 封装（为 W6 Agent 铺路）

W2 先让客户端**支持** Function Calling 协议，但业务工具（搜知识库等）留到 W6 才接。

### 3.1 协议长什么样

```python
tools = [{
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "计算数学表达式",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "如 '2+3*4'"}
            },
            "required": ["expression"]
        }
    }
}]

# 让模型决定要不要调工具
resp = client.chat_with_tools(messages, tools)
# → 如果模型想调：resp.tool_calls = [{name, arguments}]
# → 代码执行工具 → 把结果塞回 messages → 再调一次 → 模型组织最终答案
```

### 3.2 跑 demo_function_calling.py

看 `calculator` 工具怎么被模型自动调用、执行、回传，最终给出答案。这就是 Agent "长出手"的起点。

---

## 4. 怎么跑

```bash
cd "E:/AGI/WorkBuddy/2026-08-31-16-21-58/edu-pilot/week2"

# 复用 week1 的 .env（client 会自动向上找）
.venv\Scripts\python.exe demo_prompts.py            # 跑 5 个教学模板
.venv\Scripts\python.exe demo_function_calling.py   # Function Calling 最小 demo
```

---

## 5. 跑完要搞懂

1. **为什么 Prompt 要抽成模板而不是写死？**（5 条）
2. **CoT / Few-shot / 结构化输出 分别在哪个模板用？为什么？**
3. **Function Calling 的循环是什么？**（调 → 执行 → 回传 → 再调）
4. **苏格拉底式讲概念为什么不给答案？**（引导思考 > 喂答案）

---

## 6. 踩坑预警

| 坑 | 怎么避 |
|---|---|
| 结构化输出 JSON 偶尔带 markdown 代码块 ```json | 用 `response_format={"type":"json_object"}`（如果模型支持）或后处理 strip |
| Few-shot 示例本身格式不对 | 示例就是"标准答案"，模型会照抄，示例错全错 |
| 模板里 f-string 花括号冲突 | 模板尽量用 `.format()` 或明确变量，避免和 JSON 花括号混 |
| Function Calling 死循环 | 限制最大轮数（如 5 轮），防模型一直调工具 |
| 中文 prompt 被模型当英文处理 | 明确写"用中文回答"，特别结构化输出场景 |

---

## 7. 学完写 notes.md

- 5 个模板各跑一次，看输出质量
- `grade_answer` 的 JSON 能不能被 `json.loads` 解析？不能就调 prompt
- `demo_function_calling` 里模型调了几次工具？最终答案对吗？
