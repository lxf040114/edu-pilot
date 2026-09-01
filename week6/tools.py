"""工具注册（W6）：把 Python 函数暴露成 LLM 能理解的 JSON Schema，并统一分发执行。

这是「工具调用链路」的地基：
1. TOOLS：把每个工具描述成 OpenAI function-calling 的 JSON Schema（name/description/parameters）
2. FUNCTIONS：工具名 → Python 函数 的映射
3. execute(name, args)：按名字分发，捕获异常，返回字符串结果

W6 提供 3 个演示工具；W7 会加「出题/批改」等教学工具，W10 会加多 Agent 的协作工具。
"""
import ast
import glob
import json
import operator
import os
from datetime import datetime

KB_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")


# ---------- 工具实现 ----------

# calculator 用 AST 白名单安全求值，避免 eval 执行任意代码
_ALLOWED_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Pow: operator.pow,
}
_ALLOWED_UNARY = {ast.USub: operator.neg, ast.UAdd: operator.pos}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        return _ALLOWED_BINOPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_eval(node.operand))
    raise ValueError(f"不支持的表达式: {ast.dump(node)}")


def calculator(expression: str) -> str:
    """安全计算数学表达式（只允许数字 + 四则运算 + 幂 + 括号）。"""
    try:
        result = _eval(ast.parse(expression, mode="eval"))
        return str(result)
    except Exception as e:
        return f"计算失败: {e}"


def get_current_time() -> str:
    """返回当前日期时间。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S (%A)")


def search_knowledge_base(query: str) -> str:
    """在 Python 教材知识库里按关键词检索（W6 简化版：包含匹配；W7 换向量 RAG）。"""
    hits = []
    for fp in sorted(glob.glob(os.path.join(KB_DIR, "*.md"))):
        text = open(fp, encoding="utf-8").read()
        for para in text.split("\n\n"):
            if query.strip() and query.strip() in para:
                hits.append(f"[{os.path.basename(fp)}] {para.strip()[:150]}")
                break  # 每篇只取第一个命中段
    if not hits:
        return "教材里没找到与「%s」相关的内容" % query
    return "\n".join(hits[:3])


# ---------- 工具 Schema（给 LLM 看） ----------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式的值。当用户的问题需要算术计算时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如 '(5-2)+(5-2)*3' 或 '3**2'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前日期和时间。当用户问「现在几点/今天几号/星期几」时调用。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "在 Python 教材知识库里检索概念。当用户问编程概念（闭包/装饰器/递归等）时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "要检索的概念关键词，如「闭包」"}
                },
                "required": ["query"],
            },
        },
    },
]

FUNCTIONS = {
    "calculator": calculator,
    "get_current_time": get_current_time,
    "search_knowledge_base": search_knowledge_base,
}


def execute(name: str, args: dict) -> str:
    """按工具名分发执行，捕获异常，返回字符串结果。"""
    fn = FUNCTIONS.get(name)
    if fn is None:
        return f"未知工具: {name}"
    try:
        return str(fn(**args))
    except Exception as e:
        return f"工具执行出错: {e}"
