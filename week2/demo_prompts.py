"""
demo_prompts.py —— 跑 5 个教学 Prompt 模板，看输出质量。

跑：.venv/Scripts/python.exe demo_prompts.py
"""

from llm_client import LLMClient
from prompt_engine import PROMPT_REGISTRY
from prompts.grade_answer import parse_grade  # 结构化输出需要后处理


def run_one(name, messages, temperature=0.3):
    """跑一个模板，打印结果。"""
    print(f"\n{'=' * 70}")
    print(f"📌 模板：{name}")
    print(f"{'=' * 70}")
    client = LLMClient()
    resp = client.chat(messages, temperature=temperature)
    print(resp.content)
    print(f"\n[统计] tokens={resp.tokens_in + resp.tokens_out} 延迟={resp.latency_ms:.0f}ms")
    return resp


def main():
    print("EduPilot Prompt 组件库 · 5 个教学模板演示\n")

    # 1. 解题（CoT）
    run_one("solve_problem", PROMPT_REGISTRY["solve_problem"](
        question="写一个函数，输入列表返回第二大元素", student_level="初学者"))

    # 2. 出题（Few-shot）
    run_one("generate_question", PROMPT_REGISTRY["generate_question"](
        topic="递归", difficulty="中等", n=2))

    # 3. 批改（结构化输出）
    resp = run_one("grade_answer", PROMPT_REGISTRY["grade_answer"](
        question="解释什么是浅拷贝",
        student_answer="浅拷贝是复制一层，嵌套对象还是共享引用",
        reference="浅拷贝只复制顶层对象，内部嵌套对象与原对象共享同一引用"))
    # 演示：把 JSON 解析出来（真实项目要存库）
    try:
        grade = parse_grade(resp.content)
        print(f"\n✅ 解析成功：得分 {grade['score']} / 正确 {grade['correct']}")
        print(f"   漏掉：{grade['missing']}")
        print(f"   建议：{grade['advice']}")
    except ValueError as e:
        print(f"\n⚠️ JSON 解析失败：{e}（调 prompt 或加 response_format）")

    # 4. 讲概念（苏格拉底式）
    run_one("explain_concept", PROMPT_REGISTRY["explain_concept"](
        concept="递归", student_level="初学者"))

    # 5. 学习计划（结构化输出）
    resp = run_one("plan_study", PROMPT_REGISTRY["plan_study"](
        goal="掌握 Python 爬虫", weeks=4, current_level="懂基础语法"))
    try:
        import json
        plan = json.loads(resp.content.strip().strip("`").replace("json", "", 1).strip("`").strip())
        print(f"\n✅ 计划周数：{len([k for k in plan if k.startswith('week')])} 周")
    except Exception:
        print("\n（学习计划 JSON 解析略，重点看模型是否按格式输出）")

    print("\n" + "=" * 70)
    print("💡 这 5 个模板就是 EduPilot 的『Prompt 组件库』雏形")
    print("   W9 评测时，同一组题换不同模板跑，比效果")
    print("   W11 会正式沉淀成 src/components/prompts/")
    print("=" * 70)


if __name__ == "__main__":
    main()
