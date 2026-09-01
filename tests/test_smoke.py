"""EduPilot 冒烟测试：验证整合后各模块能正常 import + 基础功能。

用法（复用 week5 venv）：
  ..\\week5\\.venv\\Scripts\\python.exe tests\\test_smoke.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    from src.core.config import settings
    from src.core.llm import chat, chat_with_tools, achat, astream
    from src.rag.embedding import BGEZhEmbedding
    from src.rag.retriever import retrieve
    from src.agent.tools import TOOLS, FUNCTIONS
    from src.agent.agent import Agent
    from src.prompts.teaching import TEMPLATES
    from src.eval.metrics import keyword_hit, llm_judge
    from src.eval.evaluator import evaluate, summarize
    from src.graph.orchestration import build_graph
    print("✅ 所有模块 import 成功")


def test_tools():
    from src.agent.tools import TOOLS, FUNCTIONS
    assert len(TOOLS) == 4, "应有 4 个工具"
    assert set(FUNCTIONS) == {"search_knowledge_base", "generate_question", "grade_answer", "explain_concept"}
    print("✅ 4 个教学工具注册完整")


def test_prompts():
    from src.prompts.teaching import TEMPLATES
    assert len(TEMPLATES) == 5, "应有 5 个模板"
    s, u = TEMPLATES["solve_problem"]("什么是闭包？")
    assert "闭包" in u
    print("✅ 5 个 Prompt 模板就绪")


def test_graph():
    from src.graph.orchestration import build_graph
    g = build_graph()
    assert g is not None
    print("✅ LangGraph 图编译成功")


def test_metrics():
    from src.eval.metrics import keyword_hit
    assert keyword_hit("闭包是函数加词法作用域", ["词法作用域", "函数"]) == 1.0
    assert keyword_hit("abc", ["词法作用域"]) == 0.0
    print("✅ 指标函数正确")


if __name__ == "__main__":
    test_imports()
    test_tools()
    test_prompts()
    test_graph()
    test_metrics()
    print("\n🎉 冒烟测试全部通过")
