"""LangGraph 多 Agent 编排：讲师 → 学生 → 评估（备课→出题→答题→批改）。"""
from typing import TypedDict

from langgraph.graph import StateGraph, END

from src.core.llm import chat
from src.agent.tools import generate_question, grade_answer


class State(TypedDict):
    topic: str
    difficulty: str
    question: str
    student_answer: str
    grade: str


def simulate_student(question: str, level: str = "中等水平，答案可能不完整") -> str:
    """学生 Agent：模拟答题。"""
    system = (
        f"你现在扮演一个 Python 学生（{level}）。请回答下面的题目。"
        "用学生口吻回答，可能不完整或有点小错误，但要认真尝试。"
    )
    user = f"题目：{question}"
    text, _ = chat([{"role": "system", "content": system}, {"role": "user", "content": user}], temperature=0.7)
    return text


def lecturer_node(state: State) -> dict:
    question = generate_question(state["topic"], state.get("difficulty", "中等"))
    return {"question": question}


def student_node(state: State) -> dict:
    answer = simulate_student(state["question"])
    return {"student_answer": answer}


def grader_node(state: State) -> dict:
    grade = grade_answer(state["question"], state["student_answer"])
    return {"grade": grade}


def build_graph():
    builder = StateGraph(State)
    builder.add_node("lecturer", lecturer_node)
    builder.add_node("student", student_node)
    builder.add_node("grader", grader_node)
    builder.set_entry_point("lecturer")
    builder.add_edge("lecturer", "student")
    builder.add_edge("student", "grader")
    builder.add_edge("grader", END)
    return builder.compile()
