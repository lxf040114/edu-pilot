"""评测指标：关键词命中 + LLM-as-judge。"""
import json
import re

from src.core.llm import chat


def keyword_hit(answer: str, keywords: list[str]) -> float:
    if not keywords:
        return 0.0
    hits = [k for k in keywords if k in answer]
    return len(hits) / len(keywords)


def llm_judge(question: str, answer: str):
    system = (
        "你是严格的评测员。判断下面的回答是否准确回答了问题、是否偏离主题或编造。"
        "只输出 JSON：{\"score\": 0到10的整数, \"hallucination\": true/false}。不要解释。"
    )
    user = f"问题：{question}\n回答：{answer}"
    text, _ = chat([{"role": "system", "content": system}, {"role": "user", "content": user}], temperature=0)
    try:
        obj = json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        obj = json.loads(m.group(0)) if m else {}
    try:
        score = int(obj.get("score", 0))
    except Exception:
        score = 0
    hallucination = bool(obj.get("hallucination", False))
    return score, hallucination
