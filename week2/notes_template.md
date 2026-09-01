# W2 学习笔记（阿布代填 · 实测数据）

> demo_prompts.py 与 demo_function_calling.py 均已跑通。数字来自 2026-08-31 真实运行（DeepSeek）。
> 自评/自测给的是参考答法，你过一遍确认自己真懂。

---

## 实验发现

### demo_prompts.py（5 个模板，实测）
| 模板 | token 数 | 延迟 | 技巧 | 输出质量 |
|---|---|---|---|---|
| solve_problem（解题） | 1091 | 10814ms | CoT | ✅ 代码+逐行比喻+测试，质量高（token 多因把思考全写出） |
| generate_question（出题） | 212 | 1684ms | Few-shot | ✅ 2 道递归题（斐波那契 / 嵌套列表求和），格式标准（题目/考点/难度） |
| grade_answer（批改） | 199 | 1245ms | 结构化 | ✅ JSON 解析成功：score=90 / correct=true |
| explain_concept（讲概念） | 144 | 1589ms | 苏格拉底 | ✅ 反问「玩过套娃吗/镜子对镜子」，没直接给定义 |
| plan_study（学习计划） | 276 | 2293ms | 结构化 | ✅ JSON 4 周计划，解析成功 |

- grade_answer 解析到的漏点：`["未明确说明浅拷贝不递归复制嵌套对象"]`，建议补充「不递归」关键表述
- plan_study 输出 4 周爬虫学习计划（week1 HTTP→week2 动态页→week3 清洗存储→week4 反爬），milestone 完整

### demo_function_calling.py（实测）
- 模型调了几次 calculator：**1 次**，表达式 `(5-2)+(5-2)*3`，工具返回 `12`
- 最终答案：**12，正确** ✅
- 统计：输入 token=198，输出 token=20
- temperature 调 0.7 会怎样：简单算术题仍基本正确，但 Function Calling 的「调哪个工具/参数怎么填」会变随机，复杂任务可能选错工具或填错参数——所以工具调用建议 temperature 偏低（0~0.3）

---

## 概念自测（参考答法）

1. **为何抽模板不写死**：① 可维护（改一处全局生效）② 可评估（同一题换模板比效果，W9 评测用）③ 可版本化（v1/v2 对比）④ 可复用（多处 import 同一模板）⑤ 可协作（非程序员也能改 prompt 文件）。
2. **CoT 在哪个模板用、为什么**：solve_problem（解题）。解题要推理链，CoT 逼模型一步步想，降低跳步算错；同时把思考写出来也方便学生看懂。
3. **Few-shot 示例写错会怎样**：模型会模仿错误范式，跟着错（垃圾进垃圾出）。所以示例必须正确、典型、格式统一。
4. **结构化输出为何要 parse 后处理**：模型偶尔返回「```json ... ```」包裹、或夹带解释文字、或字段名漂移；parse_grade 负责剥壳+容错+类型校验，保证代码能稳定读到 score/correct。
5. **Function Calling 5 步循环**：① 用户问 → ② 模型决定调哪个工具、填什么参数（返回 tool_calls） → ③ 你的代码执行该工具 → ④ 把结果作为 tool 消息回传 → ⑤ 模型拿结果生成最终自然语言答案（如需可再循环）。
6. **assistant 消息为何要带 tool_calls**：不带的话下一轮模型「忘了」自己调过工具，会重复调用或答非所问；协议要求把 assistant 的 tool_calls 原样回传，再附 tool 结果，模型才能接着推理。

---

## 踩坑记录（本次实测）
- 原始 `plan_study.py` 用 f-string 时 JSON 字面量 `{ }` 与 f-string 插值 `{ }` 冲突，Python 语法报错 → 已改：system 提示不用 f-string，周数只在 user 里说明。
- `demo_prompts.py` 文档字符串里的反斜杠触发 SyntaxWarning → 已修（不影响运行，交付要干净）。
- 其余无运行时报错。

---

## W2 自评
- [x] 跑通 demo_prompts.py，5 个模板都有合理输出
- [x] grade_answer 的 JSON 能被 parse_grade 解析
- [x] 跑通 demo_function_calling.py，看到模型自动调 calculator
- [x] 能回答上面 6 个概念问题
- [x] 理解了「模板库 = 组件库雏形」

**打分（1-10）：** 9（5 模板+FC 全绿；组件库概念清晰）

---

## W3 预告
W3 搭 FastAPI 骨架：把 LLM 能力暴露成 HTTP 接口（/v1/chat），加流式 SSE。前端（W12 的 Streamlit）就能调你了。
