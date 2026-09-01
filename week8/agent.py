"""Agent 循环（W8）：多轮版 —— 支持传入历史对话，实现上下文记忆。

相比 W7 的 run(query)（每次从零开始），W8 的 run(query, history)：
- history 是之前的完整 messages（含 system 和历史 user/assistant/tool）
- 本轮在 history 基础上 append 新的 user 消息再跑循环
- 返回 (最终答案, 更新后的 messages)，更新后的 messages 作为下一轮的 history

这样「它指什么」「接着刚才说的」这类指代就能被记住。
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
    "记住对话历史，学生用「它/这个/刚才」指代时，要结合上文理解。"
)


class Agent:
    def __init__(self, tools=TOOLS, system=DEFAULT_SYSTEM, max_rounds=6, temperature=0.2):
        self.tools = tools
        self.system = system
        self.max_rounds = max_rounds
        self.temperature = temperature
        self.trace = []

    def run(self, user_query: str, history: list[dict] | None = None):
        """多轮对话：返回 (answer, new_history)。new_history 传给下一轮。"""
        messages = list(history) if history else [{"role": "system", "content": self.system}]
        messages.append({"role": "user", "content": user_query})
        self.trace = []

        for round_no in range(1, self.max_rounds + 1):
            resp = chat_with_tools(messages, self.tools, self.temperature)
            msg = resp.choices[0].message

            # 不再调工具 → 直接回答，结束本轮
            if not msg.tool_calls:
                messages.append({"role": "assistant", "content": msg.content or ""})
                self.trace.append({"round": round_no, "action": "answer", "content": msg.content})
                return msg.content or "", messages

            # 要调工具：记 assistant 的 tool_calls，执行工具，回传结果
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

        return "（达到最大轮次，仍未给出最终答案）", messages
