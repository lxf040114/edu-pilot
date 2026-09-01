"""
实验 3：Prompt 工程 —— 同一个问题，三种 Prompt 跑出不同结果。

跑：python prompt_lab.py

三种 Prompt：
1. Zero-shot —— 直接问，看模型基础能力
2. Few-shot —— 给 1-2 个示例，模型照葫芦画瓢
3. CoT  (Chain-of-Thought) —— 强制让它一步步思考

观察点：
- 回答质量
- 用了多少 token（CoT 最贵，因为它会写很多"思考过程"）
- 耗时（更长输出 = 更长耗时）
"""

from llm_client import LLMClient


QUESTION = "小明有 5 个苹果，吃了 2 个，又买了 3 倍数量的，最后有几个？"


# 三个不同 Prompt
PROMPTS = {
    "Zero-shot（直接问）": [
        {"role": "user", "content": QUESTION}
    ],

    "Few-shot（给示例）": [
        {"role": "user", "content": "小红有 10 颗糖，给了妹妹 3 颗，又买了 2 倍数量的，剩几颗？"},
        {"role": "assistant", "content": "小红原本 10 颗，减去 3 颗剩 7 颗，再乘以 2 倍即买了 14 颗，最后剩 7+14=21 颗。"},
        {"role": "user", "content": QUESTION},
    ],

    "CoT（一步步思考）": [
        {
            "role": "system",
            "content": "你是数学老师。解题时必须先一步步写出推理过程，最后再给出答案。"
        },
        {"role": "user", "content": f"{QUESTION}\n\n请一步步推理后再答。"},
    ],
}


def run():
    client = LLMClient()

    print("=" * 70)
    print(f"题目：{QUESTION}")
    print("=" * 70)

    for name, messages in PROMPTS.items():
        print(f"\n{'━' * 70}")
        print(f"📌 Prompt 策略：{name}")
        print(f"{'━' * 70}\n")

        resp = client.chat(messages, temperature=0.3)  # 数学题用低温度
        print(f"[模型回答]\n{resp.content}\n")

        print(f"─ 统计 ─")
        print(f"  输入 token = {resp.tokens_in}")
        print(f"  输出 token = {resp.tokens_out}")
        print(f"  耗时       = {resp.latency_ms:.0f} ms\n")

    print("=" * 70)
    print("💡 观察题")
    print("=" * 70)
    print("1. 哪种 Prompt 答得最对？")
    print("2. 哪种 Prompt 用 token 最多？（思考为什么）")
    print("3. Few-shot 的示例对回答风格有什么影响？")
    print("4. 数学题不上 CoT 容易算错，试试把 temperature 调到 0 看会不会更稳。")
    print()
    print("🎓 教学场景的经验法则：")
    print("   - 概念解释：Few-shot（统一风格）")
    print("   - 数学/推理：CoT（不解释都要劝它一步步想）")
    print("   - 分类/结构化：Few-shot（确保格式一致）")
    print("   - 闲聊：Zero-shot（最少 token）")


if __name__ == "__main__":
    run()
