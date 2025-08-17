import sys
import os
import streamlit as st
from memory import ask_query, ask_by_date
from utils import get_image_from_df
import datetime
import pandas as pd

# --- Setup ---
st.set_page_config(layout="centered")
st.title("The Mismatched APP")

# ✅ Load Google Sheet as CSV (published version)
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTcqUwnUPUyaXN4ZbrlUP9oRmz85k02nEH0PuS7D5sfjX5N6aPxCFYrxyWswhcNaZxmU9bJhKJUHv6u/pub?gid=0&single=true&output=csv"

@st.cache_data(show_spinner=False)
def load_sheet_data():
    return pd.read_csv(csv_url)

df = load_sheet_data()

# ✅ Session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_date" not in st.session_state:
    st.session_state["last_date"] = None
if "show_add_form" not in st.session_state:
    st.session_state["show_add_form"] = False

# 📦 Avatars
avatar_map = {
    "user": "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/main/resources/avatars/boy.png",
    "Zwan": "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/main/resources/avatars/boy.png",
    "Vita": "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/main/resources/avatars/girl.png",
    "assistant": "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/main/resources/avatars/girl.png",
}

# ✅ Display messages
for message in st.session_state["messages"]:
    role = message["role"]
    with st.chat_message(role, avatar=avatar_map.get(role)):
        if message.get("type") == "image":
            st.image(message["content"], width=300)
        else:
            st.markdown(message["content"])

# ✅ Input Row (Chat + Date + + Button)
with st.container():
    col1, col2, col3 = st.columns([5, 2, 1])
    with col1:
        user_query = st.chat_input("Send a message")
    with col2:
        date_input = st.date_input("📅", value=datetime.date(2024, 1, 11), label_visibility="collapsed")

# ✅ Handle date selection
if date_input and st.session_state["last_date"] != date_input:
    st.session_state["last_date"] = date_input
    formatted_date = f"{date_input.month}/{date_input.day}/{date_input.year}"  # M/D/YYYY

    date_prompt = f"I wanna know how beautiful the day was between us on {formatted_date}"
    st.session_state["messages"].append({"role": "user", "content": date_prompt})

    response, image_url = ask_by_date(formatted_date)
    st.session_state["messages"].append({"role": "Vita", "content": response})
    if image_url:
        st.session_state["messages"].append({
            "role": "assistant",
            "type": "image",
            "content": image_url
        })
    st.rerun()

# ✅ Chat input handling
if user_query:
    st.session_state["messages"].append({"role": "user", "content": user_query})
    response, image_url = ask_query(user_query)
    st.session_state["messages"].append({"role": "Vita", "content": response})
    st.rerun()
