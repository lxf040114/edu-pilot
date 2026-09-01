"""
模板 1：解题（Chain-of-Thought）

场景：学生发来一道编程/算法题，辅导老师一步步解答。
技巧：CoT —— 强制模型先推理再答，数学/代码题准确率明显提升。
"""


def solve_problem_prompt(question: str, student_level: str = "初学者") -> list:
    """
    生成"解题"对话 messages。

    :param question: 学生的题目
    :param student_level: 学生水平（影响比喻难度）
    :return: messages 列表，直接喂 client.chat()
    """
    system = (
        "你是 Python 辅导老师。解题必须遵循：\n"
        "1. 先判断学生最可能卡在哪一步\n"
        "2. 用 Chain-of-Thought 一步步写出推理过程\n"
        "3. 最后给可运行代码 + 逐行解释\n"
        f"学生水平：{student_level}。用他能懂的生活比喻，不要堆术语。"
    )
    user = f"题目：{question}\n\n请一步一步解答，不要直接给最终答案。"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
