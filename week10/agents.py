"""三个 Agent 的「大脑」：讲师、学生、评估。

每个 Agent 本质是「一次 LLM 调用 + 特定 prompt」。
LangGraph 负责「编排」（谁先谁后、状态怎么流转），Agent 大脑负责「干活」（出题/答题/批改）。
这就是「多智能体」的本质：不是多个进程，而是多个不同人设的 LLM 调用被编排起来。
"""
from llm import chat


def lecturer_generate_question(topic: str, difficulty: str = "中等", count: int = 1) -> str:
    """讲师 Agent：出题，返回 JSON（题目/考点/难度/参考答案）。"""
    system = (
        "你是 EduPilot 的 Python 讲师。请根据主题出一道题。"
        "只输出 JSON 对象，含字段：question(题目)、key_point(考点)、"
        "difficulty(难度)、answer(参考答案)。不要输出 JSON 之外的文字。"
    )
    user = f"主题：{topic}；难度：{difficulty}；数量：{count} 道"
    text, _ = chat([{"role": "system", "content": system}, {"role": "user", "content": user}], temperature=0.7)
    return text


def simulate_student(question: str, level: str = "中等水平，答案可能不完整") -> str:
    """学生 Agent：模拟答题（故意可能不完整/有小错，让评估 Agent 有活干）。"""
    system = (
        f"你现在扮演一个 Python 学生（{level}）。请回答下面的题目。"
        "用学生口吻回答，可能不完整或有点小错误，但要认真尝试。"
    )
    user = f"题目：{question}"
    text, _ = chat([{"role": "system", "content": system}, {"role": "user", "content": user}], temperature=0.7)
    return text


def grader_grade(question: str, student_answer: str) -> str:
    """评估 Agent：批改打分，返回 JSON（得分/对错/评语）。"""
    system = (
        "你是严格的批改老师。请根据题目和参考答案批改学生答案。"
        "只输出 JSON 对象：{score: 0-100整数, correct: true/false, feedback: 一句话评语}。"
        "不要输出 JSON 之外的文字。"
    )
    user = f"题目：{question}\n学生答案：{student_answer}"
    text, _ = chat([{"role": "system", "content": system}, {"role": "user", "content": user}], temperature=0.2)
    return text
