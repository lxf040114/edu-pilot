"""ReAct Agent 循环（多轮版）：大模型决策 + 工具执行 + 历史记忆。"""
import json

from src.core.llm import chat_with_tools
from src.agent.tools import TOOLS, execute

DEFAULT_SYSTEM = (
    "你是 EduPilot 的智能辅导老师。你可以调用工具来完成辅导："
    "学生问概念/知识点就调 search_knowledge_base 查教材；"
    "学生要出题就调 generate_question；"
    "学生提交答案要批改就调 grade_answer；"
    "学生要求讲解就调 explain_concept。"
    "查到的教材内容要如实引用，不要编造。记住对话历史。"
)


class Agent:
    def __init__(self, tools=TOOLS, system=DEFAULT_SYSTEM, max_rounds=6, temperature=0.2, max_history=20):
        self.tools = tools
        self.system = system
        self.max_rounds = max_rounds
        self.temperature = temperature
        self.max_history = max_history
        self.trace = []

    def _trim_history(self, messages: list[dict]) -> list[dict]:
        """截断历史：保留 system + 最近 max_history 条，且不在 tool 链中间切断。

        多轮对话历史会无限增长、token 超限，所以保留最近若干条。截断点调整到最近的
        user 消息，避免切断「assistant tool_calls ↔ tool 结果」的配对。
        """
        if len(messages) <= self.max_history:
            return messages
        system = messages[0] if messages[0]["role"] == "system" else None
        rest = messages[1:] if system else messages
        start = len(rest) - self.max_history
        while start > 0 and rest[start]["role"] != "user":
            start -= 1
        return ([system] if system else []) + rest[start:]

    def run(self, user_query: str, history: list[dict] | None = None):
        """多轮对话：返回 (answer, new_history)。"""
        messages = list(history) if history else [{"role": "system", "content": self.system}]
        messages.append({"role": "user", "content": user_query})
        messages = self._trim_history(messages)
        self.trace = []

        for round_no in range(1, self.max_rounds + 1):
            resp = chat_with_tools(messages, self.tools, self.temperature)
            msg = resp.choices[0].message

            if not msg.tool_calls:
                messages.append({"role": "assistant", "content": msg.content or ""})
                self.trace.append({"round": round_no, "action": "answer", "content": msg.content})
                return msg.content or "", messages

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

        return "（达到最大轮次）", messages
