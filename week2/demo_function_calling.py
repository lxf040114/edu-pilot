"""
demo_function_calling.py —— Function Calling 最小可运行示例。

这是 Agent "长出手"的起点：模型不再只能说话，能调用外部工具。

循环（核心中的核心）：
  用户问 → 模型决定调工具 → 代码执行工具 → 结果塞回 messages
        → 再调模型 → 模型组织最终答案

W6 的 Agent 就是在这个循环上加"多轮 + 多个工具 + 反思"。
"""

import json
from llm_client import LLMClient


# ---- 1. 定义一个工具 ----
def calculator(expression: str) -> str:
    """计算数学表达式，如 '2+3*4'。"""
    try:
        # 教学 demo 用 eval；真实项目要用安全表达式解析器（如 sympy）
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算出错: {e}"


# ---- 2. 工具的 JSON Schema 描述（告诉模型怎么调） ----
TOOLS = [{
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "计算一个数学表达式，支持 + - * / 和括号",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如 '2+3*4'",
                }
            },
            "required": ["expression"],
        },
    },
}]


def main():
    client = LLMClient()
    messages = [
        {"role": "user", "content": "小明有 5 个苹果，吃了 2 个，又买了 3 倍数量的，最后有几个？用计算器算。"}
    ]

    print("=" * 70)
    print("Function Calling 演示")
    print("=" * 70)
    print(f"[用户] {messages[0]['content']}\n")

    # ---- 3. 第一轮：让模型决定要不要调工具 ----
    resp = client.chat_with_tools(messages, TOOLS, temperature=0)

    if not resp.tool_calls:
        # 模型没调工具，直接答了
        print(f"[模型直接答] {resp.content}")
        return

    # ---- 4. 执行工具 + 把结果塞回 messages ----
    for call in resp.tool_calls:
        name = call["name"]
        args = json.loads(call["arguments"])  # 模型给的参数是 JSON 字符串

        print(f"[模型想调] {name}({args})")
        if name == "calculator":
            tool_result = calculator(args["expression"])
        else:
            tool_result = f"未知工具: {name}"

        print(f"[工具执行结果] {tool_result}\n")

        # 把"工具调用"和"工具结果"都加进 messages
        # 注意：assistant 的 message 要带 tool_calls，否则 API 报错
        messages.append({
            "role": "assistant",
            "content": resp.content or "",
            "tool_calls": [{
                "id": call["id"],
                "type": "function",
                "function": {"name": name, "arguments": call["arguments"]},
            }],
        })
        messages.append({
            "role": "tool",
            "tool_call_id": call["id"],
            "content": tool_result,
        })

    # ---- 5. 第二轮：带着工具结果再问模型，让它组织最终答案 ----
    final = client.chat(messages, temperature=0)
    print(f"[模型最终答案] {final.content}")
    print(f"\n[统计] 输入 token={final.tokens_in} 输出 token={final.tokens_out}")

    print("\n" + "=" * 70)
    print("💡 这就是 Function Calling 的完整循环")
    print("   W6 的 Agent = 这个循环 + 多个工具 + 多轮 + 反思")
    print("=" * 70)


if __name__ == "__main__":
    main()
