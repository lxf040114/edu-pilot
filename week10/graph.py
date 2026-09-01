"""LangGraph 多 Agent 编排：讲师 → 学生 → 评估。

核心概念（面试必问）：
- State：贯穿流程的共享状态（TypedDict），每个节点读它、返回部分更新
- Node：一个处理步骤（这里就是三个 Agent）
- Edge：节点间的连接，决定执行顺序
- Graph：编译后可以 invoke 执行，状态沿边流转

对比 W6/W7 的「单 Agent 循环」：那里是「一个 Agent 反复调工具」；
这里是「多个 Agent 各司其职、按图流转」，适合「备课→出题→答题→批改」这种分阶段流水线。
"""
from typing import TypedDict

from langgraph.graph import StateGraph, END

from agents import lecturer_generate_question, simulate_student, grader_grade


class State(TypedDict):
    topic: str
    difficulty: str
    question: str
    student_answer: str
    grade: str


def lecturer_node(state: State) -> dict:
    question = lecturer_generate_question(state["topic"], state.get("difficulty", "中等"))
    print(f"[讲师] 已出题：{question[:60]}...")
    return {"question": question}


def student_node(state: State) -> dict:
    answer = simulate_student(state["question"])
    print(f"[学生] 已作答：{answer[:60]}...")
    return {"student_answer": answer}


def grader_node(state: State) -> dict:
    grade = grader_grade(state["question"], state["student_answer"])
    print(f"[评估] 已批改：{grade[:60]}...")
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
