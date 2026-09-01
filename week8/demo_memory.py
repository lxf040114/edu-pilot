"""W8 演示：多轮对话记忆（不经过 HTTP，直接调 Agent）。

用法（复用 week5 venv）：
  ..\\week5\\.venv\\Scripts\\python.exe demo_memory.py
"""
from agent import Agent


def main():
    agent = Agent()
    history = None
    for q in ["什么是闭包？", "那它在装饰器里是怎么用的？"]:
        answer, history = agent.run(q, history)
        print("=" * 64)
        print(f"学生: {q}")
        print(f"助教: {answer}\n")
        for step in agent.trace:
            if step["action"] == "tool":
                print(f"   ⚙ {step['tool']}({step['args']}) → {step['result'][:60]}")


if __name__ == "__main__":
    main()
