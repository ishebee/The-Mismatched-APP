import streamlit as st
from memory import ask_query, ask_by_date
from utils import get_image_from_df
import datetime

st.title("The Mismatched APP")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Avatars
avatar_map = {
    "user": "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/refs/heads/main/resources/avatars/girl.png",
    "Zwan": "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/refs/heads/main/resources/avatars/boy.png",
    "assistant": "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/refs/heads/main/resources/avatars/boy.png",
}

# Display previous messages

for message in st.session_state.messages:
    role = message["role"]
    with st.chat_message(role, avatar=avatar_map.get(role, None)):
        if message.get("type") == "image":
            st.image(message["content"], width=300)
        else:
            st.markdown(message["content"])

# Layout for chat + date picker side-by-side
col1, col2 = st.columns([6, 2])
with col1:
    query = st.chat_input("Send a message")

with col2:
    date_input = st.date_input("📅", value=datetime.date(2024, 1, 11), label_visibility="collapsed", format="MM/DD/YYYY")

# 🔁 Handle chat input
if query:
    with st.chat_message("user", avatar=avatar_map["user"]):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    response, image_url = ask_query(query)
    with st.chat_message("Zwan", avatar=avatar_map["Zwan"]):
        st.markdown(response)
        if image_url:
            st.image(image_url, width=300)
            st.session_state.messages.append({"role": "assistant", "type": "image", "content": image_url})
    st.session_state.messages.append({"role": "assistant", "content": response})

# 🔁 Handle calendar input
if date_input and st.session_state.get("last_date") != date_input:
    st.session_state["last_date"] = date_input
    formatted_date = date_input.strftime("%m/%d/%Y")
    response, image_url = ask_by_date(formatted_date)

    with st.chat_message("user", avatar=avatar_map["user"]):
        st.markdown(f"I wanna know how beautiful the day was between us on {formatted_date}")
    st.session_state.messages.append({"role": "user", "content": f"I wanna know how beautiful the day was between us on {formatted_date}"})

    with st.chat_message("Zwan", avatar=avatar_map["Zwan"]):
        st.markdown(response)
        if image_url:
            st.image(image_url, width=300)
            st.session_state.messages.append({"role": "assistant", "type": "image", "content": image_url})
    st.session_state.messages.append({"role": "assistant", "content": response})