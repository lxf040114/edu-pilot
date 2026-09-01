"""EduPilot 轻量版（Streamlit Cloud 部署专用）。

去掉本地 RAG（BGE/chroma/sentence-transformers/torch 这些大依赖），只保留：
  - 普通对话
  - 出题 / 批改 / 讲概念 三个工具（Function Calling + ReAct）
  - 多轮对话记忆

这样 Streamlit Cloud 免费版能秒部署、稳定运行，不会被 torch/模型下载卡住。
完整版（含向量 RAG 查教材）见 app.py，本地跑用那个。

启动：
  streamlit run app_lite.py
"""
import json
import os

import streamlit as st
from openai import OpenAI

# ---- 读 key：环境变量（Streamlit Secrets 会注入）优先，st.secrets 兜底 ----
API_KEY = os.environ.get("DEEPSEEK_API_KEY") or st.secrets.get("DEEPSEEK_API_KEY", "")
BASE_URL = os.environ.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com/v1"
MODEL = os.environ.get("DEEPSEEK_MODEL") or "deepseek-chat"


@st.cache_resource
def get_client():
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


def chat(messages, temperature=0.7):
    resp = get_client().chat.completions.create(model=MODEL, messages=messages, temperature=temperature)
    return resp.choices[0].message.content or ""


def chat_with_tools(messages, tools, temperature=0.2):
    return get_client().chat.completions.create(model=MODEL, messages=messages, tools=tools, temperature=temperature)


# ---------- 三个教学工具 ----------

def generate_question(topic, difficulty="中等", count=1):
    system = (
        "你是 EduPilot 的 Python 出题老师。请根据主题出题。"
        "只输出 JSON 数组，每题含：question、key_point、difficulty、answer。"
    )
    user = f"主题：{topic}；难度：{difficulty}；数量：{count} 道"
    return chat([{"role": "system", "content": system}, {"role": "user", "content": user}], 0.7)


def grade_answer(question, student_answer):
    system = (
        "你是批改老师。请根据题目批改学生答案。"
        "只输出 JSON：{score: 0-100整数, correct: true/false, feedback: 一句话评语}。"
    )
    user = f"题目：{question}\n学生答案：{student_answer}"
    return chat([{"role": "system", "content": system}, {"role": "user", "content": user}], 0.2)


def explain_concept(concept):
    system = (
        "你是 EduPilot 的 Python 老师。请通俗讲解概念："
        "① 一句话定义 ② 生活化类比 ③ 最小代码示例。"
    )
    user = f"概念：{concept}"
    return chat([{"role": "system", "content": system}, {"role": "user", "content": user}], 0.7)


TOOLS = [
    {"type": "function", "function": {
        "name": "generate_question",
        "description": "根据主题出练习题。当用户要求「出题/给我几道题」时调用。",
        "parameters": {"type": "object", "properties": {
            "topic": {"type": "string", "description": "题目主题"},
            "difficulty": {"type": "string", "description": "难度：简单/中等/困难"},
            "count": {"type": "integer", "description": "题目数量"}
        }, "required": ["topic"]},
    }},
    {"type": "function", "function": {
        "name": "grade_answer",
        "description": "批改学生答案，给出得分和评语。",
        "parameters": {"type": "object", "properties": {
            "question": {"type": "string", "description": "题目"},
            "student_answer": {"type": "string", "description": "学生答案"}
        }, "required": ["question", "student_answer"]},
    }},
    {"type": "function", "function": {
        "name": "explain_concept",
        "description": "通俗讲解一个概念。当用户要求「讲一下/解释/什么是XX」时调用。",
        "parameters": {"type": "object", "properties": {
            "concept": {"type": "string", "description": "要讲解的概念"}
        }, "required": ["concept"]},
    }},
]

FUNCTIONS = {"generate_question": generate_question, "grade_answer": grade_answer, "explain_concept": explain_concept}


def execute(name, args):
    fn = FUNCTIONS.get(name)
    if fn is None:
        return f"未知工具: {name}"
    try:
        return str(fn(**args))
    except Exception as e:
        return f"工具执行出错: {e}"


# ---------- ReAct Agent 循环 ----------

SYSTEM = (
    "你是 EduPilot 的智能辅导老师。你可以调用工具："
    "学生要出题就调 generate_question；学生提交答案要批改就调 grade_answer；"
    "学生要求讲解就调 explain_concept。记住对话历史。"
)


def run_agent(query, history=None):
    messages = list(history) if history else [{"role": "system", "content": SYSTEM}]
    messages.append({"role": "user", "content": query})
    for _ in range(6):
        resp = chat_with_tools(messages, TOOLS)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content or ""})
            return msg.content or "", messages
        tool_calls = [
            {"id": tc.id, "type": "function",
             "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in msg.tool_calls
        ]
        messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": tool_calls})
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = execute(name, args)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    return "（达到最大轮次）", messages


# ---------- UI ----------

st.set_page_config(page_title="EduPilot 智能助教", page_icon="🎓", layout="wide")
st.title("🎓 EduPilot 智能助教")
st.caption("AI 教育实训平台 · 教学辅导 Agent（Function Calling + ReAct + 多轮记忆）")

with st.sidebar:
    st.header("我能做什么")
    st.markdown("- ✍️ **出题**：说「给我出 2 道递归题」")
    st.markdown("- 📝 **批改**：把题目和学生答案一起发我")
    st.markdown("- 💡 **讲概念**：说「讲一下装饰器」")
    st.markdown("- 💬 **答疑**：问 Python 问题")
    st.divider()
    st.caption("轻量版：纯 LLM，不含本地向量 RAG")
    if st.button("🧹 清空对话", use_container_width=True):
        st.session_state.history = None
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = None

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if not API_KEY:
    st.error("未检测到 DEEPSEEK_API_KEY，请在 Streamlit 的 Settings → Secrets 里配置。")

if prompt := st.chat_input("问我 Python 问题，或让我出题 / 批改 / 讲概念"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("思考中…"):
            answer, history = run_agent(prompt, st.session_state.history)
            st.session_state.history = history
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
