import sys
import os
try:
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")  # Force updated SQLite
except ImportError:
    print("⚠️ pysqlite3-binary is missing. Install it using `pip install pysqlite3-binary`.")
import streamlit as st
from memory import ask_query, ask_by_date
from utils import get_image_from_df
import datetime


st.set_page_config(layout="centered")
st.title("The Mismatched APP")

# Session state initialization
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_date" not in st.session_state:
    st.session_state["last_date"] = None

# 📦 Avatars
avatar_map = {
    "user": "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/refs/heads/main/resources/avatars/girl.png",
    "Zwan": "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/refs/heads/main/resources/avatars/boy.png",
    "assistant": "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/refs/heads/main/resources/avatars/boy.png",
}

# 📬 Handle all messages from session state
for message in st.session_state["messages"]:
    role = message["role"]
    with st.chat_message(role, avatar=avatar_map.get(role)):
        if message.get("type") == "image":
            st.image(message["content"], width=300)
        else:
            st.markdown(message["content"])

# ✅ Input section at the very bottom after messages
with st.container():
    col1, col2 = st.columns([6, 2])
    with col1:
        user_query = st.chat_input("Send a message")
    with col2:
        date_input = st.date_input(
            "📅",
            value=datetime.date(2024, 1, 11),
            label_visibility="collapsed",
            format="MM/DD/YYYY"
        )

# 📅 Process date selection only if changed
if date_input and st.session_state["last_date"] != date_input:
    st.session_state["last_date"] = date_input
    formatted_date = date_input.strftime("%m/%d/%Y")

    date_prompt = f"I wanna know how beautiful the day was between us on {formatted_date}"
    st.session_state["messages"].append({"role": "user", "content": date_prompt})

    response, image_url = ask_by_date(formatted_date)
    st.session_state["messages"].append({"role": "Zwan", "content": response})
    if image_url:
        st.session_state["messages"].append({
            "role": "assistant",
            "type": "image",
            "content": image_url
        })
    st.rerun()

# 💬 Handle chat input
if user_query:
    if user_query:
        st.session_state["messages"].append({"role": "user", "content": user_query})
        response, _ = ask_query(user_query)  # Ignore image
        st.session_state["messages"].append({"role": "Zwan", "content": response})
        st.rerun()
