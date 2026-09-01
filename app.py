"""EduPilot Streamlit 前端：教学辅导 Agent 对话界面。

关键设计：Agent（含 BGE 模型 + Chroma）用 st.cache_resource 懒加载，
首屏只渲染 UI 秒开，避免"一进来就卡在模型加载"导致白屏。

启动（复用 week5 venv）：
  ..\\week5\\.venv\\Scripts\\python.exe -m streamlit run app.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

st.set_page_config(page_title="EduPilot 智能助教", page_icon="🎓", layout="wide")

st.title("🎓 EduPilot 智能助教")
st.caption("AI 教育实训平台 · 教学辅导 Agent（RAG + ReAct + 多轮记忆）")

# ---- 侧边栏 ----
with st.sidebar:
    st.header("我能做什么")
    st.markdown("- 📚 **查教材**：问 Python 概念（闭包/装饰器/递归…）")
    st.markdown("- ✍️ **出题**：说「给我出 2 道递归题」")
    st.markdown("- 📝 **批改**：把题目和学生答案一起发我")
    st.markdown("- 💡 **讲概念**：说「讲一下装饰器」")
    st.divider()
    st.caption("向量 RAG（BGE-zh）+ ReAct Agent + LangGraph")
    if st.button("🧹 清空对话", use_container_width=True):
        st.session_state.history = None
        st.session_state.messages = []
        st.rerun()


# ---- 懒加载 Agent（首次发消息才加载 BGE 模型 + Chroma，避免白屏）----
@st.cache_resource
def get_agent():
    from src.agent.agent import Agent
    return Agent()


# ---- 会话状态 ----
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = None

# ---- 历史消息 ----
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ---- 输入 ----
if prompt := st.chat_input("问我 Python 问题，或让我出题 / 批改 / 讲概念"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中…（首次会加载模型，稍等）"):
            answer, history = get_agent().run(prompt, st.session_state.history)
            st.session_state.history = history
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
