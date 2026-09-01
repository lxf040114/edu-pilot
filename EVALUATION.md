# 评测体系（Evaluation）

> 对应 JD「测试数据集 + 基线对比 + A/B 实验」。完整实现见 [`week9/`](./week9/)，数据见 [`data/eval_data.json`](./data/eval_data.json)。

## 一、测试数据集

8 道教学问答 + 参考关键词，覆盖闭包 / 装饰器 / 递归 / 列表推导式四个知识点。

## 二、评测指标（两个互补）

| 指标 | 说明 | 特点 |
|---|---|---|
| 关键词命中率 | 参考答案关键词在模型回答中出现比例 | 客观、可复现 |
| LLM-as-judge | 用 LLM 给回答打 0-10 分 + 判断是否编造 | 更接近"真懂" |

## 三、A/B 实验设计

| 版本 | 做法 |
|---|---|
| 基线（无 RAG） | 直接问 LLM，不带教材 |
| 变体（基础 RAG） | BGE 向量检索 top3 + 教材上下文 |
| 进阶（进阶 RAG） | Multi-Query + Rerank 精排 |

## 四、关键发现（完整闭环）

1. **发现缺陷**：基础 RAG 在碎片化切片上反而拖后腿（评委 7.9、编造 12%）
2. **试检索算法**：上 Multi-Query + Rerank，没修复
3. **定位根因**：切片按空行切太碎，答案内容被切散在多个 chunk
4. **修复验证**：改按 markdown 标题切片后，评委 7.9 → 9.1、编造 12% → 0%

> 详细过程见 [`week9/DEEP_DIVE.md`](./week9/DEEP_DIVE.md)，含面试讲法。

## 五、运行

```bash
# 两方对比（无 RAG vs 基础 RAG）
week5\.venv\Scripts\python.exe week9\run_eval.py

# 三方对比（无 RAG vs 基础 RAG vs 进阶 RAG）
week5\.venv\Scripts\python.exe week9\run_eval_v2.py
```
