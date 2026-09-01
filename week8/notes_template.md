# W8 学习笔记（智能答疑系统）

> 已用真实运行数据填好（2026-08-31 跑 `test_api.py`）

## 一、核心概念自测（参考答案）

1. 多轮记忆的本质是什么？
   答：**保存并回传完整的 messages 历史**（含 system、历史的 user/assistant/tool）。
   每轮把历史 + 新问题一起发给模型，模型就「记得」之前聊过什么。

2. history 里为什么连 tool 消息也要保存？
   答：模型下一轮要「记得」自己调过什么工具、结果是什么。tool 消息必须和 assistant 的
   tool_calls 配对（协议要求，见 W2 笔记第 6 条），否则会重复调用或上下文断裂。

3. session_id 是干嘛的？
   答：多用户/多会话隔离。不同 session 各存一份独立历史，互不干扰；同一 session 连续调用即多轮。

4. 多轮历史会不会无限增长？怎么处理？
   答：会。轮数越多 token 越长，可能超限。处理：截断（只保留最近 N 轮）、摘要压缩（旧对话压成
   一段摘要）、或滑动窗口。W9/W11 会做。

5. Agent 从「单轮」到「多轮」，代码上改了什么？
   答：`run(query)` → `run(query, history)`；messages 从「每次新建 [system, user]」变成
   「history + 新 user」，最后返回更新后的 messages 作为下一轮 history。

## 二、实测：多轮记忆验证

运行命令：`..\week5\.venv\Scripts\python.exe test_api.py`

- health 返回：`{'status': 'ok', 'active_sessions': 0}`
- 第 1 轮「什么是闭包」→ 讲闭包定义：「函数 + 它记住的外部变量」的组合
- 第 2 轮「那它在装饰器里怎么用」→ ✅ **正确理解了「它=闭包」**，直接答「闭包在装饰器中的应用」并引教材「装饰器底层就是闭包」
- 流式接口 content-type：`text/event-stream; charset=utf-8`，收到 `[DONE]`
- reset 后会话：`{'status': 'ok', 'session_id': 'stu_001'}`

结论：多轮记忆工作正常——第二轮模型没有重新解释「闭包是什么」，而是接住上下文直接讲应用。

## 三、踩坑记录

- 无大坑。关键点：history 里必须原样保留 assistant 的 tool_calls + 对应的 tool 消息，否则下一轮
  模型会「失忆」或重复调工具。
- 简化流式：W8 的 stream 是「Agent 跑完拿答案再分块返回」，不是 token 级；真正的 token 级流式在
  Agent+工具场景留到 W11。

## 四、本周自评（1-10）

W8 掌握度：9 / 10
扣分原因：① 流式是「答案分块」简化版 ② 历史无截断，长对话会涨 token（W9/W11 补）。
