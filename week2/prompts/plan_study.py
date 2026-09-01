"""
模板 5：学习计划（结构化输出）

场景：根据目标/周期/水平，生成每周学习计划。
技巧：结构化输出 —— JSON，方便前端渲染成卡片、存库、做进度跟踪。

注意：system 提示词里不要写 f-string 花括号，JSON 的 { } 会和 f-string 的 { } 冲突。
      所以 weeks 数量只放在 user 里说明，system 用泛化的 "week1、week2...weekN" 描述格式。
"""


def plan_study_prompt(goal: str, weeks: int, current_level: str = "零基础") -> list:
    """
    生成"学习计划"对话 messages。

    :param goal: 学习目标，如 "掌握 Python 爬虫"
    :param weeks: 总周数
    :param current_level: 当前水平
    :return: messages 列表
    """
    system = (
        "你是学习规划师。输出严格只一个 JSON 对象，不要 markdown 代码块，不要任何解释文字。\n"
        "字段规则：week1、week2、...、weekN 各自对应一周的主题与任务，"
        "最后额外加一个 milestone 字段表示结业能达到的标准。\n"
        "示例结构：{\"week1\": \"...\", \"week2\": \"...\", \"milestone\": \"...\"}"
    )
    user = (
        f"目标：{goal}\n"
        f"周期：{weeks} 周\n"
        f"当前水平：{current_level}\n\n"
        f"请输出 week1 到 week{weeks} 的计划 JSON（含 milestone 字段）。"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
