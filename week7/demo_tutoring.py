"""W7 演示：教学辅导 Agent（覆盖四个教学工具）。

用法（复用 week5 的 venv，因为向量 RAG 需要 torch/chroma）：
  ..\\week5\\.venv\\Scripts\\python.exe demo_tutoring.py
"""
from agent import Agent


def main():
    agent = Agent()
    scenarios = [
        "给我出 2 道关于递归的练习题",
        "讲一下什么是装饰器",
        "闭包是什么？它为什么能记住外部变量？",
        "题目：什么是列表推导式？学生答：列表推导式就是 for 循环的简写。请批改并点评",
    ]
    for q in scenarios:
        print("=" * 64)
        print(f"学生/老师: {q}")
        answer = agent.run(q)
        print(f"助教: {answer}\n")
        for step in agent.trace:
            if step["action"] == "tool":
                print(f"   ⚙ 调用工具 {step['tool']}({step['args']}) → {step['result'][:80]}")
        print()


if __name__ == "__main__":
    main()
