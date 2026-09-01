# W1 学习笔记（阿布代填 · 实测数据）

> 3 个实验均已跑通。下面数字来自 2026-08-31 真实运行（DeepSeek，model=deepseek-chat）。
> 自评和自测答法是我给的「参考答法」，你过一遍确认自己真懂。

---

## 实验发现

### hello_llm.py
- provider / model：`deepseek` / `deepseek-chat`（deepseek-chat 内部别名 deepseek-v4-flash，正常）
- 体验：HTTP 200，回答「闭包就像一个带记忆的背包…」，质量通顺
- 实测统计：输入 token = 36，输出 token = 30，耗时 = 2135 ms
- temperature=0 vs 1.5：闭包比喻题对 temperature 不敏感（语义题）；但数学/代码题建议 temperature=0 更稳，减少胡编

### stream_chat.py（实测）
| 模式 | 首字到达 | 总耗时 | 说明 |
|---|---|---|---|
| A 一次性（同步） | 2636ms 才出 | 2636ms | 用户干等 |
| B 流式（同步） | **747ms** | 1388ms | 边生成边吐，体感快 |
| C 4 并发（异步） | — | **1180ms** | 4 题同时跑，吞吐≈单题 |

- 单个问题延迟样本：1001 / 921 / 915 / 1155 ms
- 结论：流式 = 用户体感快；并发 = 系统吞吐高（W9 评测一次跑 200 题就靠它）；FastAPI 同时用 SSE + async 才快

### prompt_lab.py（实测，题目：5苹果吃2又买3倍，剩几个？）
| Prompt 策略 | 输入 token | 输出 token | 耗时 | 答案 |
|---|---|---|---|---|
| Zero-shot | 29 | 149 | 3173 ms | 12 ✅ |
| Few-shot | 102 | 134 | 1509 ms | 12 ✅ |
| CoT | 52 | 162 | 1554 ms | 12 ✅ |

- 三者都答对（题简单）。CoT 输出 token 最多（162）——因为它把思考过程也写出来
- 经验法则：概念解释用 Few-shot（统一风格）；数学/推理用 CoT；分类/结构化用 Few-shot；闲聊用 Zero-shot

---

## 概念自测（参考答法）

1. **LLM 的本质**：一个「下一个 token 的预测器」。给定前面一串字，它算概率分布，采样出最可能接着出现的那个字，循环往复。它不「理解」，是在做统计续写。
2. **为什么对齐后才会聊天**：预训练只学了「续写互联网文本」；经过 SFT（监督微调）+ RLHF（人类反馈强化学习）对齐后，才学会按「对话格式」、按人类偏好来续写，于是表现为「聊天」。
3. **system / user / assistant 三 role 关系**：system 是给模型的「人设/规则」（优先级最高，不进对话可见流）；user 是用户每轮输入；assistant 是模型上一轮的回复。多轮就是把历史 assistant+user 依次塞回 messages，模型据此续写。
4. **temperature=0 vs =2**：0 = 几乎贪心选最高概率，输出稳定可复现，适合数学/代码/判分；高温度 = 更随机有创意，适合写故事/头脑风暴。数学题用 0。
5. **流式输出什么协议**：服务端用 SSE（Server-Sent Events，text/event-stream）或分块 HTTP 传输，模型每生成一个 token 就 flush 一块给客户端，前端逐块渲染，所以「边生成边显示」。本质是分块传输 + 前端增量渲染。
6. **国产模型为何能用 openai SDK**：它们实现了 OpenAI 的 Chat Completions API 协议（请求/响应字段一致），只改 `base_url`（如 https://api.deepseek.com/v1）即可，代码零改动。
7. **Few-shot vs CoT 场景**：Few-shot = 给几个「输入→输出」范例，让模型模仿格式/风格（分类、统一话术、出题）；CoT = 让模型「一步步想」，把推理链写出来再给答案，适合数学、逻辑、多步推理。

---

## 踩坑记录（本次实测）
- 无代码报错。唯一一次 401 是早期 `.env` 里 key 还是占位符，填真 key 后解决。
- ⚠️ 安全提醒：你的 DeepSeek key 曾明文出现在聊天里，建议去控制台 rotate 掉，新 key 只填进 `.env`（已在 .gitignore）。

---

## W1 自评
- [x] 配好环境、装好依赖、跑通 3 个实验
- [x] 能回答上面的 7 个概念问题
- [x] 理解了 system / user / assistant 三种 role
- [x] 理解了 temperature 和 stream 的作用
- [x] 理解了 OpenAI 兼容协议原理

**打分（自己评 1-10）：** 8（环境+3实验+原理都过；rotate key 这步待办）

---

## W2 预告
W2 把「写死」的 Prompt 抽成「模板」，扩出 5 个教学场景专属模板（解题/出题/批改/讲概念/学习计划），并给客户端加 Function Calling 封装。
