"""
Streamlit teacher UI:
- chat interface that calls the FastAPI /chat endpoint
- course insights page

This gives you a real UI layer and portfolio signal.
"""

import requests
import streamlit as st
import pandas as pd

API_BASE = st.sidebar.text_input("API base URL", "http://localhost:8000")

st.set_page_config(page_title="Teacher AI Assistant", layout="wide")
st.title("🧑‍🏫 Teacher Performance AI Assistant")

tab_chat, tab_course = st.tabs(["Chat", "Course Insights"])

with tab_chat:
    st.subheader("Ask about student performance")

    teacher_id = st.text_input("Teacher ID", "T1")
    course_id = st.text_input("Course ID", "C1")

    if "history" not in st.session_state:
        st.session_state.history = []

    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_msg = st.chat_input("Try: How is student S100123 doing in my course?")
    if user_msg:
        st.session_state.history.append({"role": "user", "content": user_msg})
        with st.chat_message("user"):
            st.markdown(user_msg)

        payload = {
            "teacher_id": teacher_id,
            "course_id": course_id,
            "message": user_msg,
            "history": [{"role": m["role"], "content": m["content"]} for m in st.session_state.history[-8:]],
        }
        r = requests.post(f"{API_BASE}/chat", json=payload, timeout=30)
        r.raise_for_status()
        resp = r.json()

        st.session_state.history.append({"role": "assistant", "content": resp["answer"]})
        with st.chat_message("assistant"):
            st.markdown(resp["answer"])
            if resp.get("suggested_followups"):
                st.caption("Suggested follow-ups:")
                for s in resp["suggested_followups"]:
                    st.write(f"- {s}")

with tab_course:
    st.subheader("Course insights")
    course_id = st.text_input("Course ID (insights)", "C1", key="course_insights_id")

    if st.button("Load insights"):
        r = requests.get(f"{API_BASE}/courses/{course_id}/insights", timeout=30)
        r.raise_for_status()
        data = r.json()

        st.write("### Struggling students (top 10)")
        ss = pd.DataFrame(data["struggling_students"])
        st.dataframe(ss, use_container_width=True)

        st.write("### Hardest assignments")
        ha = pd.DataFrame(data["hardest_assignments"])
        st.dataframe(ha, use_container_width=True)
