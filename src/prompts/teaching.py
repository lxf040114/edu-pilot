"""教学 Prompt 模板库：5 个业务模板，覆盖核心教学场景。

每个模板返回 (system, user) 两条消息，方便调用方组装。
技巧对应：解题=CoT、出题=Few-shot、批改/计划=结构化输出、讲概念=苏格拉底式。
"""


def solve_problem(question: str) -> tuple[str, str]:
    """解题：CoT，让模型一步步想，写出推理链。"""
    system = (
        "你是 EduPilot 的 Python 助教。解题时请【一步一步思考】，"
        "先分析题目，再给出解题思路，最后给代码和逐行解释。"
    )
    user = f"题目：{question}\n请一步步解答。"
    return system, user


def generate_question(topic: str, difficulty: str = "中等", count: int = 1) -> tuple[str, str]:
    """出题：Few-shot + 结构化输出，返回 JSON 数组。"""
    system = (
        "你是 EduPilot 的出题老师。请根据主题出题。"
        "只输出 JSON 数组，每题含：question、key_point、difficulty、answer。"
    )
    user = f"主题：{topic}；难度：{difficulty}；数量：{count} 道"
    return system, user


def grade_answer(question: str, student_answer: str) -> tuple[str, str]:
    """批改：结构化输出，返回 JSON {score, correct, feedback}。"""
    system = (
        "你是批改老师。请根据题目批改学生答案。"
        "只输出 JSON：{score: 0-100整数, correct: true/false, feedback: 一句话评语}。"
    )
    user = f"题目：{question}\n学生答案：{student_answer}"
    return system, user


def explain_concept(concept: str) -> tuple[str, str]:
    """讲概念：苏格拉底式引导 + 生活化类比，不直接塞定义。"""
    system = (
        "你是 EduPilot 的 Python 老师。讲解概念时先问一个引导性问题，"
        "再用生活化类比，最后给最小代码示例。不要一上来就甩定义。"
    )
    user = f"概念：{concept}"
    return system, user


def plan_study(goal: str, weeks: int = 4) -> tuple[str, str]:
    """学习计划：结构化输出，返回 JSON 周计划。"""
    system = (
        "你是学习规划师。请制定学习计划，只输出 JSON 数组，"
        "每项含：week(第几周)、theme(主题)、tasks(任务列表)、milestone(里程碑)。"
    )
    user = f"目标：{goal}；时长：{weeks} 周"
    return system, user


TEMPLATES = {
    "solve_problem": solve_problem,
    "generate_question": generate_question,
    "grade_answer": grade_answer,
    "explain_concept": explain_concept,
    "plan_study": plan_study,
}
