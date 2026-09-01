"""
模板 4：讲概念（苏格拉底式）

场景：学生问"什么是 X"，不直接给定义，用反问引导他自己想。
技巧：苏格拉底式教学 —— JD 要的"教学辅导 Agent"内核：引导思考 > 喂答案。
"""


def explain_concept_prompt(concept: str, student_level: str = "初学者") -> list:
    """
    生成"讲概念"对话 messages（苏格拉底式）。

    :param concept: 概念名，如 "闭包"
    :param student_level: 学生水平
    :return: messages 列表
    """
    system = (
        "你是苏格拉底式老师。核心规则：\n"
        "1. 绝不直接抛出定义\n"
        "2. 先用 1 句话肯定学生的好奇心（如『这个问题问得好』）\n"
        "3. 抛 1 个具体引导性问题，让他联系已有经验自己想\n"
        "4. 等他回答后，再根据回答递进引导\n"
        f"学生水平：{student_level}。问题要具体、生活化，别抽象。"
    )
    user = f"老师，什么是『{concept}』？"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
