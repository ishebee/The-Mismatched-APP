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
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

# === Google Sheets setup ===
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDENTIALS_PATH"), scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(os.getenv("SHEET_ID")).sheet1

# Load sheet data into DataFrame
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.set_page_config(layout="centered")
st.markdown("""
    <style>
        .input-row {display: flex; flex-wrap: wrap; gap: 0.5rem;}
        .input-row > div {flex-grow: 1;}
        @media only screen and (max-width: 600px) {
            .input-row {flex-direction: column;}
        }
    </style>
""", unsafe_allow_html=True)

st.title("The Mismatched APP")

# Session state initialization
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

# Display messages
for message in st.session_state["messages"]:
    role = message["role"]
    with st.chat_message(role, avatar=avatar_map.get(role)):
        if message.get("type") == "image":
            st.image(message["content"], width=300)
        else:
            st.markdown(message["content"])

# Input row: Chat + Date + Add button
st.markdown('<div class="input-row">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([6, 2, 1])
with col1:
    user_query = st.chat_input("Send a message")
with col2:
    date_input = st.date_input("📅", value=datetime.date(2024, 1, 11), label_visibility="collapsed")
with col3:
    if st.button("➕"):
        st.session_state["show_add_form"] = not st.session_state["show_add_form"]
st.markdown('</div>', unsafe_allow_html=True)

# Add memory form
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
            records = sheet.get_all_records()
            match_found = False

            for i, row in enumerate(records):
                if (
                    row["Date"] == new_date_str
                    and row["Event"] == new_event
                    and row["Tag"] == new_tag
                ):
                    new_mem = row["Memory"] + " " + new_memory
                    new_img = new_image or row.get("Image", "")
                    sheet.update_cell(i+2, 1, new_mem)  # A: Memory
                    sheet.update_cell(i+2, 5, new_img)  # E: Image
                    match_found = True
                    break

            if not match_found:
                new_row = [new_memory, new_date_str, new_event, new_tag, new_image or ""]
                sheet.append_row(new_row)

            st.session_state["show_add_form"] = False
            st.success("Memory added/updated successfully!")
            st.rerun()

# Handle date selection
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
