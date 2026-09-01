"""教学工具：把 EduPilot 的教学能力封装成 Agent 可调用的工具（含 JSON Schema + 分发）。

四个工具对应 JD「教学辅导 Agent / 智能答疑」：
- search_knowledge_base：向量 RAG 检索教材
- generate_question：出题
- grade_answer：批改
- explain_concept：讲概念
"""
from src.core.llm import chat
from src.rag.retriever import retrieve


def search_knowledge_base(query: str) -> str:
    """向量 RAG 检索教材，返回最相关片段（只召回、不生成）。"""
    chunks = retrieve(query, top_k=3)
    if not chunks:
        return "教材里没找到相关内容"
    return "\n".join(f"[{m['source']}] {t[:150]}" for t, m, _ in chunks)


def generate_question(topic: str, difficulty: str = "中等", count: int = 1) -> str:
    system = (
        "你是 EduPilot 的 Python 出题老师。请根据主题出题。"
        "只输出 JSON 数组，每题含字段：question(题目)、key_point(考点)、"
        "difficulty(难度)、answer(参考答案)。不要输出 JSON 之外的文字。"
    )
    user = f"主题：{topic}；难度：{difficulty}；数量：{count} 道"
    text, _ = chat([{"role": "system", "content": system}, {"role": "user", "content": user}], temperature=0.7)
    return text


def grade_answer(question: str, student_answer: str) -> str:
    system = (
        "你是批改老师。请根据题目批改学生答案。"
        "只输出 JSON：{score: 0-100整数, correct: true/false, feedback: 一句话评语}。"
        "不要输出 JSON 之外的文字。"
    )
    user = f"题目：{question}\n学生答案：{student_answer}"
    text, _ = chat([{"role": "system", "content": system}, {"role": "user", "content": user}], temperature=0.2)
    return text


def explain_concept(concept: str) -> str:
    system = (
        "你是 EduPilot 的 Python 老师。请通俗讲解概念："
        "① 先用一句话给定义 ② 再用一个生活化类比 ③ 最后给一个最小代码示例。"
    )
    user = f"概念：{concept}"
    text, _ = chat([{"role": "system", "content": system}, {"role": "user", "content": user}], temperature=0.7)
    return text


TOOLS = [
    {"type": "function", "function": {
        "name": "search_knowledge_base",
        "description": "在 Python 教材知识库里做向量语义检索。当学生问编程概念/知识点时调用。",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "要检索的问题或概念"}
        }, "required": ["query"]},
    }},
    {"type": "function", "function": {
        "name": "generate_question",
        "description": "根据主题出练习题。当用户要求「出题/给我几道题/练习」时调用。",
        "parameters": {"type": "object", "properties": {
            "topic": {"type": "string", "description": "题目主题"},
            "difficulty": {"type": "string", "description": "难度：简单/中等/困难"},
            "count": {"type": "integer", "description": "题目数量"}
        }, "required": ["topic"]},
    }},
    {"type": "function", "function": {
        "name": "grade_answer",
        "description": "批改学生答案，给出得分和评语。",
        "parameters": {"type": "object", "properties": {
            "question": {"type": "string", "description": "题目"},
            "student_answer": {"type": "string", "description": "学生的答案"}
        }, "required": ["question", "student_answer"]},
    }},
    {"type": "function", "function": {
        "name": "explain_concept",
        "description": "通俗讲解一个概念。当用户要求「讲一下/解释/什么是XX」时调用。",
        "parameters": {"type": "object", "properties": {
            "concept": {"type": "string", "description": "要讲解的概念"}
        }, "required": ["concept"]},
    }},
]

FUNCTIONS = {
    "search_knowledge_base": search_knowledge_base,
    "generate_question": generate_question,
    "grade_answer": grade_answer,
    "explain_concept": explain_concept,
}


def execute(name: str, args: dict) -> str:
    fn = FUNCTIONS.get(name)
    if fn is None:
        return f"未知工具: {name}"
    try:
        return str(fn(**args))
    except Exception as e:
        return f"工具执行出错: {e}"
