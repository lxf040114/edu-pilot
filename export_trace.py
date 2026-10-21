"""导出一条真实 Agent 多轮对话的完整 trace 到 docs/sample_trace.md。

用途：把「输入 → 工具调用/参数 → 工具返回 → 最终答案」的完整链路落盘，作为面试/评审材料，
回答"四个工具、session 记忆如何实际协作"。

跑法（先确保已装依赖、且 .env 或 week1/.env 里配了 DEEPSEEK_API_KEY）：
    cd edu-pilot
    ..\\week5\\.venv\\Scripts\\python.exe export_trace.py
（没有 week5 venv 就用你本机的 python： python export_trace.py）

说明：
- 三段式对话，尽量覆盖 检索(search_knowledge_base) / 出题(generate_question) /
  批改(grade_answer) / 讲概念(explain_concept) 四类工具，实际调哪个由模型决定，如实记录。
- search_knowledge_base 需要本地 Chroma + BGE 模型（sentence-transformers）；若不想触发它，
  把第 1 轮的问法换成"讲一下装饰器"这类纯概念问题即可。
- 生成的文件是 docs/sample_trace.md，请自查确认内容真实无误后再提交。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.agent import Agent


def _fmt(v) -> str:
    return json.dumps(v, ensure_ascii=False, indent=2)


def main():
    agent = Agent()

    turns = [
        "什么是闭包？它为什么能记住外部变量？",
        "给我出 2 道中等难度的递归练习题。",
        "我答一下这道题：递归必须具备哪两个要素？我的回答是：结束条件 和 重复调用自己。请批改。",
    ]

    out = ["# EduPilot Agent 真实调用 trace", ""]
    out.append(
        "> 模型：DeepSeek（deepseek-chat）· Agent：Function Calling + ReAct 循环（最多 6 轮）"
        "· 多轮记忆：同一 session 的完整 messages 历史（含 tool 消息）逐轮回传。"
    )
    out.append("")

    history = None
    for idx, q in enumerate(turns, 1):
        answer, history = agent.run(q, history)

        out.append(f"## 第 {idx} 轮")
        out.append("")
        out.append(f"**用户输入**：{q}")
        out.append("")
        out.append("**工具调用过程**：")
        if not agent.trace:
            out.append("- （本轮未调用工具，模型直接回答）")
        else:
            for step in agent.trace:
                if step["action"] == "tool":
                    out.append(f"- 调用工具 `{step['tool']}`")
                    out.append(f"  - 参数：`{_fmt(step['args'])}`")
                    out.append(f"  - 返回：`{_fmt(step['result'])}`")
                else:
                    out.append("- 生成最终答案")
        out.append("")
        out.append("**最终答案**：")
        out.append("")
        out.append(str(answer).strip())
        out.append("")
        out.append("---")
        out.append("")

    os.makedirs("docs", exist_ok=True)
    path = os.path.join("docs", "sample_trace.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"已生成 {path}")


if __name__ == "__main__":
    main()
