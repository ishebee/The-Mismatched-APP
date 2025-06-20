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
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(layout="centered")
st.title("The Mismatched APP")

# ✅ Google Sheets Setup
SHEET_ID = "your_actual_sheet_id_here"  # Hardcoded Sheet ID
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1uCozg_MtU2UllwZa4VXidADeUS-TbV4RZ38VYfbddII").sheet1

# Load sheet as DataFrame
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_date" not in st.session_state:
    st.session_state["last_date"] = None
if "show_add_form" not in st.session_state:
    st.session_state["show_add_form"] = False

# Avatars
avatar_map = {
    "user": "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/main/resources/avatars/girl.png",
    "Zwan": "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/main/resources/avatars/boy.png",
    "assistant": "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/main/resources/avatars/boy.png",
}

# Show all previous messages
for message in st.session_state["messages"]:
    role = message["role"]
    with st.chat_message(role, avatar=avatar_map.get(role)):
        if message.get("type") == "image":
            st.image(message["content"], width=300)
        else:
            st.markdown(message["content"])

# Chat input + Date + Add Memory in one row
with st.container():
    st.markdown("""
        <style>
        .input-row {
            display: flex;
            flex-direction: row;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        .input-row > div {
            flex: 1;
            min-width: 150px;
        }
        </style>
        <div class="input-row">
            <div id="chat_input"></div>
            <div id="date_input"></div>
            <div id="add_button"></div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([5, 2, 1])
    with col1:
        user_query = st.chat_input("Send a message", key="chat_input_box")
    with col2:
        date_input = st.date_input("📅", value=datetime.date(2024, 1, 11), label_visibility="collapsed", key="date_input_box")
    with col3:
        if st.button("➕", key="add_btn"):
            st.session_state["show_add_form"] = not st.session_state["show_add_form"]

# Show memory add form
if st.session_state["show_add_form"]:
    with st.form("add_memory_form"):
        new_memory = st.text_area("Memory", placeholder="Write your memory here")
        new_date = st.date_input("Date", value=datetime.date.today())
        new_event = st.text_input("Event", placeholder="Birthday, Trip, etc.")
        new_tag = st.text_input("Tag", placeholder="Love, Fun, Sadness, etc.")
        new_image = st.text_input("Image URL (optional)")
        submitted = st.form_submit_button("Submit")

        if submitted:
            new_date_str = f"{new_date.month}/{new_date.day}/{new_date.year}"  # M/D/YYYY

            # Update or append row in DataFrame
            mask = (
                (df["Date"] == new_date_str)
                & (df["Event"] == new_event)
                & (df["Tag"] == new_tag)
            )

            if mask.any():
                df.loc[mask, "Memory"] += f" {new_memory}"
                if new_image:
                    df.loc[mask, "Image"] = new_image
            else:
                new_row = {
                    "Memory": new_memory,
                    "Date": new_date_str,
                    "Event": new_event,
                    "Tag": new_tag,
                    "Image": new_image or ""
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # Upload new df to Google Sheets
            sheet.clear()
            sheet.update([df.columns.values.tolist()] + df.values.tolist())

            st.session_state["show_add_form"] = False
            st.success("Memory added/updated successfully!")
            st.rerun()

# Handle date-based question
if date_input and st.session_state["last_date"] != date_input:
    st.session_state["last_date"] = date_input
    formatted_date = f"{date_input.month}/{date_input.day}/{date_input.year}"

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

# Handle chat input
if user_query:
    st.session_state["messages"].append({"role": "user", "content": user_query})
    response, image_url = ask_query(user_query)
    st.session_state["messages"].append({"role": "Zwan", "content": response})
    st.rerun()
