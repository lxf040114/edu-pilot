"""Agent 循环（W6 核心）：ReAct 模式。

ReAct = Reasoning（推理）+ Acting（行动）交替：
  1. 用户提问
  2. 模型「推理」出：这个问题我需要调哪个工具、传什么参数？→ 返回 tool_calls
  3. 代码「行动」：执行工具，拿到结果
  4. 把结果作为 tool 消息回传给模型
  5. 模型结合结果「再推理」，要么继续调下一个工具，要么给出最终答案

循环直到：模型不再返回 tool_calls（直接回答），或达到最大轮次（防止死循环）。

对应 JD 的「Agent 多轮 + Function Calling + 工具调用链路」。
"""
import json

from llm import chat_with_tools
from tools import TOOLS, execute

DEFAULT_SYSTEM = (
    "你是 EduPilot 的智能助教。你可以调用工具来回答问题："
    "需要算数就调 calculator，需要时间就调 get_current_time，"
    "需要查编程概念就调 search_knowledge_base。"
    "查到的教材内容要如实引用，不要编造。"
)


class Agent:
    def __init__(self, tools=TOOLS, system=DEFAULT_SYSTEM, max_rounds=6, temperature=0.2):
        self.tools = tools
        self.system = system
        self.max_rounds = max_rounds
        self.temperature = temperature
        self.trace = []  # 记录每一步（调了哪些工具、结果如何），方便学习/调试/评测

    def run(self, user_query: str) -> str:
        messages = [
            {"role": "system", "content": self.system},
            {"role": "user", "content": user_query},
        ]
        self.trace = []

        for round_no in range(1, self.max_rounds + 1):
            resp = chat_with_tools(messages, self.tools, self.temperature)
            msg = resp.choices[0].message

            # 情况 A：模型不再调工具，直接回答 → 结束
            if not msg.tool_calls:
                self.trace.append({"round": round_no, "action": "answer", "content": msg.content})
                return msg.content or ""

            # 情况 B：模型要调工具
            # 1) 把 assistant 的 tool_calls 原样记进历史（协议要求，见 W2 笔记第 6 条）
            tool_calls = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ]
            messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": tool_calls})

            # 2) 逐个执行工具，把结果作为 tool 消息回传
            for tc in msg.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = execute(name, args)
                self.trace.append({"round": round_no, "action": "tool", "tool": name, "args": args, "result": result})
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

        # 达到最大轮次还没收敛（少见，说明模型一直在调工具或参数有问题）
        return "（达到最大轮次，仍未给出最终答案）"
