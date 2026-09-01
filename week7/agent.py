"""Agent 循环（W7）：ReAct 模式，工具换成教学工具。

与 W6 完全相同的循环结构，只是工具变成了教学能力——这就是「教学辅导 Agent」：
大模型负责决策「该出题还是该批改还是该查教材」，工具负责具体执行。
"""
import json

from llm import chat_with_tools
from tutoring_tools import TOOLS, execute

DEFAULT_SYSTEM = (
    "你是 EduPilot 的智能辅导老师。你可以调用工具来完成辅导："
    "学生问概念/知识点就调 search_knowledge_base 查教材；"
    "学生要出题就调 generate_question；"
    "学生提交答案要批改就调 grade_answer；"
    "学生要求讲解就调 explain_concept。"
    "查到的教材内容要如实引用，不要编造。"
)


class Agent:
    def __init__(self, tools=TOOLS, system=DEFAULT_SYSTEM, max_rounds=6, temperature=0.2):
        self.tools = tools
        self.system = system
        self.max_rounds = max_rounds
        self.temperature = temperature
        self.trace = []

    def run(self, user_query: str) -> str:
        messages = [
            {"role": "system", "content": self.system},
            {"role": "user", "content": user_query},
        ]
        self.trace = []

        for round_no in range(1, self.max_rounds + 1):
            resp = chat_with_tools(messages, self.tools, self.temperature)
            msg = resp.choices[0].message

            if not msg.tool_calls:
                self.trace.append({"round": round_no, "action": "answer", "content": msg.content})
                return msg.content or ""

            tool_calls = [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ]
            messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": tool_calls})

            for tc in msg.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = execute(name, args)
                self.trace.append({"round": round_no, "action": "tool", "tool": name, "args": args, "result": result})
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

        return "（达到最大轮次，仍未给出最终答案）"
