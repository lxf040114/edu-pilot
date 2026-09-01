# W1 · LLM API 入门

> 目标：**让 LLM 听你使唤**。装好环境、调通对话、看懂流式、做 Prompt 实验。

---

## 1. 学什么（30 分钟）

### 1.1 LLM 是什么、能干什么

- **LLM（大语言模型）**：用海量文本训练出来的"下一个 token 预测器"。给它一段上文，它预测下一个字，把预测出的字接上去再预测下下个，反复循环就能"写字"。
- **它的本质**：一个非常复杂的条件概率分布 P(下一个token | 上文)。所以"理解"、"推理"、"创作"都只是训练数据里的统计模式。
- **为什么它能对话**：被"对齐"过（RLHF），会按人类期望回答问题，而不只是续写句子。

> 💡 一句话：**LLM 是接龙高手，对齐让它成了聊天机器人**。

### 1.2 LLM API 的统一接口

不管 OpenAI、DeepSeek、通义千问、智谱、Anthropic Claude（新版兼容），调用模式都长这样：

```python
client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是老师"},
        {"role": "user",   "content": "解释闭包"}
    ],
    temperature=0.7,
    stream=False
)
```

**核心结构**：
| 字段 | 含义 |
|---|---|
| `model` | 用哪个模型（影响能力 + 价格） |
| `messages` | 对话历史，由 role + content 组成 |
| `temperature` | 0 = 严谨/确定，1 = 发散/创造性，2 = 乱讲 |
| `stream` | True 就一字一字返回（流式），False 一次性返回 |
| `max_tokens` | 限制输出长度（省钱 + 防止失控） |

**`messages` 里的 role**：
- `system` —— 给模型的"人设/规则"，告诉它怎么回答
- `user` —— 人类的问题
- `assistant` —— 模型之前的回答（多轮对话时塞回上下文）

### 1.3 流式输出 (SSE)

问"为什么流式？"
- **等模型把 500 字全部生成完再返回** → 用户看着白屏干等 10 秒
- **一边生成一边推** → 立刻开始显示，体验"打字机"效果

技术上是 **Server-Sent Events (SSE)**，HTTP 长连接，每个 chunk 一行。

### 1.4 Token 与成本

LLM 按 token 计费：
- 英文：1 token ≈ 4 个字母 或 0.75 个单词
- 中文：1 token ≈ 1-1.5 个汉字
- 输入 + 输出 都算钱

举例：DeepSeek-chat 价格约 ¥1/百万输入 token，¥2/百万输出 token。一次 1000 字问答约 ¥0.005。

**省钱技巧**：精简 prompt、控制 max_tokens、不用贵的模型搞简单任务。

### 1.5 Prompt 工程基础

| 技巧 | 用法 | 场景 |
|---|---|---|
| **Zero-shot** | 直接问 | 简单任务 |
| **Few-shot** | 给 2-3 个示例 | 分类、风格模仿 |
| **CoT** (Chain-of-Thought) | 加"Let's think step by step" | 数学、推理 |
| **结构化输出** | 让模型按 JSON Schema 输出 | 程序化处理 |

---

## 2. 怎么跑（10 分钟）

### 2.1 安装依赖

```bash
cd edu-pilot/week1

# 推荐用 venv 隔离环境
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2.2 配置 API Key

复制 `.env.example` 为 `.env`，填上你的 key：

```bash
# DeepSeek（推荐，价格低、能力强、走 OpenAI 协议）
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY
```

支持的 provider 切换（在 `.env` 里改 `LLM_PROVIDER`）：
- `deepseek` —— DeepSeek（默认推荐）
- `qwen` —— 通义千问（DashScope）
- `glm` —— 智谱 GLM
- `openai` —— OpenAI（如果你也搞到了 key）

> 没有 key？告诉我，我加一个 mock 模式。

### 2.3 跑 3 个实验

```bash
python hello_llm.py     # 实验1：基本对话
python stream_chat.py   # 实验2：流式输出
python prompt_lab.py    # 实验3：3 个 Prompt 对比同一问题
```

---

## 3. 文件说明

| 文件 | 干嘛的 |
|---|---|
| `llm_client.py` | **核心**。统一封装 LLM 调用，支持国产模型 + OpenAI，一处切换 |
| `hello_llm.py` | 实验 1：最基本的"我说一句话，AI 回一句" |
| `stream_chat.py` | 实验 2：流式打字机效果，对比同步 vs 异步 |
| `prompt_lab.py` | 实验 3：同一个问题，3 种 Prompt 跑出不同结果 |
| `requirements.txt` | 依赖（openai、python-dotenv） |
| `.env.example` | 环境变量模板 |

---

## 4. 跑完后要搞懂的几件事

完成 W1 后，你应该能答出来：

1. **LLM 调用接口是什么结构？** → messages / model / temperature / stream
2. **system / user / assistant 三种 role 干嘛的？** → 人设/人类/AI历史回答
3. **temperature 怎么影响输出？** → 0 严谨、1 发散、2 随机
4. **流式输出技术上是什么？** → SSE（Server-Sent Events）
5. **国产模型走什么协议？** → OpenAI 兼容协议（统一 SDK 接口）
6. **Few-shot 和 CoT 什么时候用？** → Few-shot 分类/模仿、CoT 数学/推理

---

## 5. 踩坑预警

| 坑 | 怎么避 |
|---|---|
| API key 泄露到 git | 用 `.env` + 加进 `.gitignore`；客户端代码只 `os.getenv` 不硬编码 |
| 调通了但很贵 | 默认模型在 `.env` 改便宜的那档（如 deepseek-chat 而不是 deepseek-reasoner） |
| 输出截断了 | 调大 `max_tokens`，或检查 Prompt 让它"说短一点" |
| 流式只看到一坨 | 用了 `stream=True` 但用 `.content` 取值；改用迭代 chunk 才能逐字显示 |
| 国产模型用 OpenAI SDK 调不通 | 检查 `LLM_BASE_URL` 是否对，每个厂商不一样（见 `.env.example`） |
| 中文乱码 | `.env` 用 UTF-8 保存；终端是 Windows 且没改编码可能乱，输出本来就 UTF-8 |

---

## 6. 学完写 `notes.md`

跑通 3 个实验后，把你的发现写到 `notes.md`：
- `temperature` 0/0.7/1.5 跑同一个 Prompt，分别什么效果？
- Few-shot 比 Zero-shot 多花了多少 token？效果好了多少？
- 流式比同步体感快多少？

这一份笔记 12 周后回头看，是成长记录。
