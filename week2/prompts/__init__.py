"""Prompt 模板包的统一出口。"""

from .solve_problem import solve_problem_prompt
from .generate_question import generate_question_prompt
from .grade_answer import grade_answer_prompt
from .explain_concept import explain_concept_prompt
from .plan_study import plan_study_prompt

__all__ = [
    "solve_problem_prompt",
    "generate_question_prompt",
    "grade_answer_prompt",
    "explain_concept_prompt",
    "plan_study_prompt",
]
