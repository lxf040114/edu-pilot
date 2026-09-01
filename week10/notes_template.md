# W10 学习笔记（LangGraph 多 Agent 编排）

> 已用真实运行数据填好（2026-08-31 跑 `run.py`）

## 一、核心概念自测（参考答案）

1. LangGraph 的 State / Node / Edge 分别是什么？
   答：**State** = 贯穿流程的共享状态（topic→question→student_answer→grade）；
   **Node** = 一个处理步骤（一个 Agent）；**Edge** = 节点间的连接，决定执行顺序。

2. 多 Agent 和单 Agent 的本质区别？
   答：单 Agent = 一个 LLM 反复调工具（自己决策自己干）；多 Agent = 多个**不同人设的 LLM 调用**
   按图编排、各司其职。本质是「分工协作」vs「单打独斗」。

3. 什么场景适合多 Agent 编排（而不是单 Agent）？
   答：**分阶段流水线**（备课→出题→批改、写作→审校→发布）适合多 Agent，每阶段职责清晰、可独立替换；
   单任务、交互式问答适合单 Agent。

4. 状态（State）为什么是「显式」的，好处是什么？
   答：每个节点读 State、返回部分更新，状态流动**清晰可见、可调试、可检查点恢复**；
   单 Agent 的 messages 是隐式状态，不易追踪。

5. 「多智能体」是不是就是「多个进程/多个模型」？
   答：不是。多智能体通常是**同一个模型 + 多个不同 prompt 人设**，被编排成协作流程，不是多个独立进程。

## 二、实测：多 Agent 流程结果

运行命令：`..\week5\.venv\Scripts\python.exe run.py`

- 讲师出的题：`sum_digits(n)` 递归求各位数字之和（含考点/难度/参考答案，JSON 完整）
- 学生答案：学生口吻、有思考过程，代码正确，还自己验证了 `sum_digits(1234)=10`
- 评估批改：`{"score": 100, "correct": true, "feedback": "递归实现正确，基线条件和递推关系均符合要求"}`

结论：三个 Agent 按「讲师→学生→评估」的图正确流转，状态（topic→question→answer→grade）传递无误。

## 三、踩坑记录

- langgraph 首次安装**静默失败**：`websockets.exe` 写入失败（sandbox 回收站不可用），错误被 `tail -5`
  吞掉没看见，重装才成功。教训：装包报错要看完整输出，不能只看 tail。
- langgraph 1.2.11 的 `StateGraph(State) + TypedDict + add_node/add_edge/compile/invoke` API 与标准用法兼容。

## 四、本周自评（1-10）

W10 掌握度：9 / 10
扣分原因：只做了线性流水线（讲师→学生→评估），没展示条件分支/循环等进阶图结构（如「评估不合格→打回重答」）。
