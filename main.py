import streamlit as st

def ask(query):
    return "Hello"

st.title("The Mismatched APP")

query = st.chat_input("Waiting for your message")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if query:
    with st.chat_message("user",avatar="Avatar/girl.png"):
        st.markdown(query)
    st.session_state.messages.append({"role":"user", "content":query})

    response = ask(query)
    with st.chat_message("Vita",avatar="Avatar/boy.png"):
        st.markdown(response)
        st.image("https://drive.google.com/uc?export=view&id=1QoNIYeK6qcCqmhD0RZUtdsnHyU2qJ-sl", width=300)
    st.session_state.messages.append({"role": "assistant", "content": response})