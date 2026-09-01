"""
实验 1：LLM API 最基本的调用。

目标：
- 能构造一次对话
- 能拿到回复
- 看到 token 和延迟

跑：python hello_llm.py
"""

from llm_client import LLMClient


def main():
    # 1. 初始化客户端（自动读 .env，切换 provider 改 LLM_PROVIDER 即可）
    client = LLMClient()
    print(f"\n[已加载] provider={client.cfg['provider']} model={client.cfg['model']}\n")

    # 2. 构造对话 —— 这就是 LLM API 最核心的"messages"
    messages = [
        # system：模型的人设/规则，会作为对话的"前置条件"
        {
            "role": "system",
            "content": "你是一名 Python 老师，专门给零基础学生讲课。"
                       "回答问题要用最简单的比喻，不要堆术语，不超过 80 字。"
        },
        # user：用户的提问
        {
            "role": "user",
            "content": "什么是闭包？"
        },
    ]

    # 3. 发起调用
    print("[用户问] " + messages[-1]["content"])
    print("[模型答]\n")
    resp = client.chat(messages, temperature=0.3)  # 教学场景用低温度，让它稳

    # 4. 输出
    print(resp.content)
    print()
    print("─" * 50)
    print(f"📊 本次调用")
    print(f"   模型       = {resp.model}")
    print(f"   输入 token = {resp.tokens_in}")
    print(f"   输出 token = {resp.tokens_out}")
    print(f"   耗时       = {resp.latency_ms:.0f} ms (~{resp.latency_ms/1000:.1f}s)")
    print()
    print("🎯 试试改 messages 里的 system content，看回答风格怎么变；")
    print("   改 temperature（0/0.7/1.5），看回答确定性怎么变。")


if __name__ == "__main__":
    main()
