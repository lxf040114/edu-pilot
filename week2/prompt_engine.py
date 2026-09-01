"""
Prompt 模板引擎 —— 把所有教学 Prompt 集中管理。

设计：
- 每个模板是一个函数，接收业务参数，返回 messages 列表
- 主程序 import 后直接喂给 client.chat()
- 模板带模块级文档字符串，新人一看就懂

为什么不直接在业务代码里写字符串？
见 week2/README.md 第 1 节：可维护 / 可评估 / 可版本化 / 可复用。
"""

from prompts import (
    solve_problem_prompt,
    generate_question_prompt,
    grade_answer_prompt,
    explain_concept_prompt,
    plan_study_prompt,
)

# 模板注册表：名字 → 函数，方便按名字调用（W9 评测时用到）
PROMPT_REGISTRY = {
    "solve_problem": solve_problem_prompt,
    "generate_question": generate_question_prompt,
    "grade_answer": grade_answer_prompt,
    "explain_concept": explain_concept_prompt,
    "plan_study": plan_study_prompt,
}


def get_prompt(name: str, **kwargs):
    """按名字取模板并渲染。"""
    if name not in PROMPT_REGISTRY:
        raise KeyError(f"未知模板: {name}。可用: {list(PROMPT_REGISTRY.keys())}")
    return PROMPT_REGISTRY[name](**kwargs)


# 列出所有模板名（调试用）
def list_prompts():
    return list(PROMPT_REGISTRY.keys())


if __name__ == "__main__":
    print("可用 Prompt 模板：")
    for name in list_prompts():
        print(f"  - {name}")
