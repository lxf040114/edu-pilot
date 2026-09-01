"""W6 演示：Agent 多步工具调用（含一次「多工具协同」）。

用法：
  .venv/Scripts/python.exe demo_agent.py
"""
from agent import Agent


def main():
    agent = Agent()
    queries = [
        "帮我算一下 (5-2)+(5-2)*3 等于多少？",
        "现在几点了？",
        "闭包是什么？它为什么能记住外部变量？",
        "先算 3 的平方，再告诉我今天是星期几",  # 一次问题里要用两个工具
    ]
    for q in queries:
        print("=" * 64)
        print(f"用户: {q}")
        answer = agent.run(q)
        print(f"助手: {answer}")
        # 打印工具调用轨迹，看清 Agent 每一步做了什么
        for step in agent.trace:
            if step["action"] == "tool":
                print(f"   ⚙ 调用工具 {step['tool']}({step['args']}) → {step['result'][:60]}")
        print()


if __name__ == "__main__":
    main()
