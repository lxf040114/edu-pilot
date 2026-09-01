"""
模板 3：批改（结构化输出）

场景：学生交了作业，自动批改并给分。
技巧：结构化输出 —— 强制 JSON，方便存库、算班级平均分、做评测。
"""

import json


def grade_answer_prompt(question: str, student_answer: str, reference: str) -> list:
    """
    生成"批改"对话 messages。

    :param question: 原题
    :param student_answer: 学生写的答案
    :param reference: 标准答案（或参考答案要点）
    :return: messages 列表
    """
    system = (
        "你是批改老师。按维度打分并给改进建议。\n"
        "必须严格只输出一个 JSON 对象，不要 markdown 代码块，不要解释：\n"
        '{"score": <0-100整数>, "correct": <true或false>, '
        '"missing": ["学生漏掉的关键点"], "advice": "具体改进建议"}'
    )
    user = (
        f"题目：{question}\n"
        f"学生答案：{student_answer}\n"
        f"标准答案：{reference}\n\n"
        "请输出 JSON 批改结果。"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def parse_grade(json_text: str) -> dict:
    """
    把模型返回的（可能带 ```json 的）文本解析成 dict。
    这是实际项目里必备的后处理——模型偶尔不老实。
    """
    text = json_text.strip()
    if text.startswith("```"):
        # 去掉 ```json ... ``` 包裹
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"模型没返回合法 JSON: {e}\n原始文本: {json_text}")
