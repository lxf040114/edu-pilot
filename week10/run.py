"""W10 演示：多 Agent 协同「备课→出题→答题→批改」全流程。

用法（复用 week5 venv，已装 langgraph）：
  ..\\week5\\.venv\\Scripts\\python.exe run.py
"""
from graph import build_graph


def main():
    graph = build_graph()
    print("=" * 64)
    print("运行多 Agent 流程：讲师出题 → 学生答题 → 评估批改\n")
    result = graph.invoke({"topic": "递归", "difficulty": "中等"})

    print("=" * 64)
    print("【讲师出题】")
    print(result["question"])
    print("\n【学生作答】")
    print(result["student_answer"])
    print("\n【评估批改】")
    print(result["grade"])
    print("=" * 64)


if __name__ == "__main__":
    main()
