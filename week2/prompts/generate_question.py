"""
模板 2：出题（Few-shot）

场景：老师要针对某个知识点出 N 道题。
技巧：Few-shot —— 给 1 个标准示例，模型照格式输出，保证可机器解析。
"""


def generate_question_prompt(topic: str, difficulty: str = "简单", n: int = 3) -> list:
    """
    生成"出题"对话 messages。

    :param topic: 知识点，如 "装饰器"
    :param difficulty: 难度档位（简单/中等/困难）
    :param n: 出题数量
    :return: messages 列表
    """
    system = "你是资深 Python 出题老师。严格按照示例格式输出，不要多余废话。"

    # Few-shot 示例：这就是"标准答案格式"，模型会照抄结构
    few_shot = [
        {
            "role": "user",
            "content": "给『列表』出 1 道简单题",
        },
        {
            "role": "assistant",
            "content": (
                "【题目】如何用一个列表存 5 个学生的成绩，并求平均分？\n"
                "【考点】列表遍历、sum()、len()\n"
                "【难度】简单"
            ),
        },
    ]

    user = f"给『{topic}』出 {n} 道{difficulty}题，沿用上面的格式（每题含【题目】【考点】【难度】）。"
    return [
        {"role": "system", "content": system},
        *few_shot,
        {"role": "user", "content": user},
    ]
