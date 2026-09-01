# W5 · RAG 进阶：中文嵌入 + 重排序 + 多查询

> 承接 W4。W4 用 Chroma 自带英文 MiniLM 做嵌入，实测中文检索排序差（「闭包」的定义排到第 5）。
> W5 用三板斧根治它，并量化对比提升。

## 一、W4 到底哪错了

W4 问「什么是闭包」，正确定义在 `闭包.md` 里，但 MiniLM 把它排到了第 5 位——因为
`all-MiniLM-L6-v2` 是**英文**模型，中文句子的向量空间是「扭曲」的，语义距离不可信。

这不是调 `top_k` 能解决的（W4 只是把 top_k 从 3 调到 5 临时糊过去了）。**embedding 质量才是命门。**

## 二、三板斧（对应 JD「RAG 知识库」进阶能力）

### 1. 换中文嵌入：BGE-zh
- 用 `BAAI/bge-small-zh-v1.5`（BGE 系列，专为中文训练的双塔嵌入模型）。
- **关键细节**：BGE 做检索时，查询侧要加指令前缀
  `为这个句子生成表示以用于检索相关文章：`
  不加会掉点（这是 BGE 官方用法）。
- 文档侧不用加前缀。

### 2. Multi-Query 多查询
- 学生口语化提问（"闭包咋记住变量的？"）和教材书面语（"闭包是…的引用环境"）之间
  存在「语义鸿沟」。
- 让 LLM 把问题改写成 3 个不同表述的查询，每个查询各召回 top-5，合并去重 → 召回更全，
  漏检率下降。
- 代价：多调几次 LLM（延迟略增），但换来了召回率。

### 3. Rerank 重排序
- 双塔（bi-encoder，如 BGE-zh）为了**速度**，把 query 和 doc 各自编码后算余弦——但它
  看不到 query 和 doc 之间的**交互**，排序只是「近似」。
- 交叉编码（cross-encoder，如 `bge-reranker-base`）把 `(query, doc)` 拼成一段喂给模型，
  逐对精算相关性 → **准**，但慢（不能对全库做，只能对召回出来的候选做）。
- 所以工业级 RAG 是**两段式**：bi-encoder 召回（快、粗）→ cross-encoder 精排（慢、准）。

## 三、目录结构

```
week5/
├── config.py            # 读 .env（向上复用 week1 的 key）
├── llm.py               # LLM 客户端（比 week3 多了同步 chat，给 Multi-Query 用）
├── embedding.py         # BGEZhEmbedding：BGE-zh 包装成 Chroma 的 embedding_function
├── rag_advanced.py      # 核心：ingest / retrieve_baseline / retrieve_zh /
│                        #      multi_query_generate / rerank / retrieve_multi_query / ask
├── main.py              # FastAPI：/health、/v1/rag/advanced、/v1/rag/advanced/stream
├── test_rag_advanced.py # 量化对比脚本（W4基线 vs 仅换嵌入 vs 完整进阶）
├── knowledge_base/      # 4 篇教材（闭包/装饰器/递归/列表推导式）
└── notes_template.md    # 学习笔记（跑完填真实数据）
```

## 四、怎么跑

```bash
cd "E:/AGI/WorkBuddy/2026-08-31-16-21-58/edu-pilot/week5"

# 1. 建 venv + 装依赖（torch 较大，建议用国内镜像）
python -m venv .venv
.venv\Scripts\activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 2. 首次跑会用 HF 镜像下载模型（bge-small-zh ~130MB + bge-reranker-base ~450MB）
#    Windows 下设置 HF_ENDPOINT 走镜像，避免下载卡住：
set HF_ENDPOINT=https://hf-mirror.com
.venv\Scripts\python.exe test_rag_advanced.py

# 3. 起服务看接口
.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
# 浏览器开 http://127.0.0.1:8000/docs
```

## 五、你该懂的（面试能答）

1. 为什么中文 RAG 不能用英文 embedding 模型？
2. BGE 检索为什么要加指令前缀？
3. bi-encoder（双塔）和 cross-encoder（交叉）的本质区别？
4. 为什么工业 RAG 是「召回 + 重排」两段式，而不是一步到位？
5. Multi-Query 解决什么问题、有什么代价？

（答案在 `notes_template.md` 里，跑完填。）

## 六、下一步（W6）

Agent 入门：给 LLM 加 Function Calling 循环，让它能「自己决定调用工具」——
这是 JD「Agent 多轮 + 工具调用链路」的起点，也是 W7 教学辅导 Agent 的地基。
