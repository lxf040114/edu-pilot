# W4 · RAG 基础（检索增强生成）

> 目标：把「通用聊天」升级成「基于教材的助教」。先检索相关知识，再让 LLM 照着回答。
> 这是 JD 里「RAG 知识库」的核心，也是 EduPilot 真正有壁垒的一步。

---

## RAG 是什么（一句话）
**Retrieval-Augmented Generation**：不让 LLM 凭记忆瞎答，而是先从一个「知识库」里查出和问题最相关的几段，拼进 prompt，让模型**只依据这些资料**回答。

## 为什么需要它
- LLM 训练数据有截止日期，新知识它不知道
- 容易「幻觉」（编造）
- 你的教材/讲义是私有知识，模型没见过

RAG 让模型「开卷考试」，答案可追溯、可控制。

---

## 这条链路的 5 步
```
教材 .md
  → ① 切片(chunk)：按空行切成小段
  → ② 向量化(embed)：每段变成一个向量
  → ③ 入库(Chroma)：向量存进向量数据库
  → ④ 检索(retrieve)：把用户问题也向量化，找最相似的 top-k 段
  → ⑤ 增强生成(augment+generate)：top-k 段拼进 prompt，调 LLM 回答
```

---

## 目录结构
```
week4/
├── main.py              # FastAPI：/v1/rag（先检索再答）+ /v1/rag/stream
├── rag.py               # RAG 核心：切片/入库/检索/拼 prompt（复用 week3 的 llm）
├── knowledge_base/      # 4 篇 Python 教材（闭包/装饰器/递归/列表推导式）
├── test_rag.py          # 离线验证全链路
├── test_api.py          # 验证 /v1/rag 接口
├── requirements.txt
├── .gitignore           # 含 .chroma/
└── notes_template.md
```

---

## 怎么跑
```bash
cd "E:/AGI/WorkBuddy/2026-08-31-16-21-58/edu-pilot/week4"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

.venv\Scripts\python.exe test_rag.py     # 全链路
.venv\Scripts\python.exe test_api.py     # 接口
```

起服务看 Swagger：
```bash
.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
# http://127.0.0.1:8000/docs
```

---

## ⚠️ 本周年会看到的「真问题」（也是 W5 要修的）
W4 用的是 Chroma 自带 **ONNX MiniLM** 嵌入模型——它是**英文**模型，中文语义弱。
实测：问「什么是闭包」，模型把「递归.md」排到第 1，闭包的正确定义被排到第 5（距离 0.45）。
→ 如果 top_k=3，定义没被召回，模型会答「教材没讲这部分」。
→ 我们把这个小知识库的 top_k 调到 5 才答对。

**根因**：嵌入模型中文不行，检索排序不准。
**W5 的解法**：换成中文嵌入（如 BGE-zh / m3e）+ 重排序（rerank），检索质量会明显提升，top_k 也能降回来。

---

## 概念自测（看笔记）
1. RAG 为什么能减少幻觉？
2. 切片粒度太粗 / 太细各有什么坏处？
3. 向量检索的「距离」越小代表什么？
4. 为什么还要把检索结果拼回 prompt，而不是直接返回？
5. top_k 调大能解决一切吗？（不能——根本在 embedding 质量）

---

## W5 预告
W5 RAG 进阶：中文嵌入模型 + 重排序（rerank）+ 多查询（Multi-Query），把检索准确率做上去。
