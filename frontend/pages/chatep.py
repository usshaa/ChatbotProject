import streamlit as st
import requests

API_URL = "http://localhost:5000/chat"

st.set_page_config(
    page_title="Chatbot",
    page_icon="https://img.icons8.com/?size=100&id=aIYDmrSk6X13&format=png&color=000000",
    layout="wide"
)

st.title("Simple stateless chatbot")

if "simple_messages" not in st.session_state:
    st.session_state.simple_messages = []

with st.sidebar:
    st.header("Request Setting")
    system_prompt = st.text_area(
        "System Instruction",
        value="You are a helpful AI assistant",
        height=80
    )
    max_tokens = st.slider("Max New Tokens",min_value=16, max_value=256, value=100, step=16)
    temperature = st.slider("Temperature",min_value=0.0, max_value=1.0, value=0.7, step=0.1)

    if st.button("Clear chat history",use_container_width=True):
        st.session_state.simple_messages = []
        st.rerun()

for msg in st.session_state.simple_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Enter your message")

if user_input:
    st.session_state.simple_messages.append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    formatted_payload = [{"role":"system","content":system_prompt}]
    for m in st.session_state.simple_messages:
        formatted_payload.append({"role":m["role"],"content":m["content"]})

    with st.chat_message("assistant"):
        with st.spinner("Generating reply"):
            try:
                payload = {
                    "messages":formatted_payload,
                    "max_tokens":max_tokens,
                    "temperature": temperature
                }
                headers = {"Content-Type":"application/json"}

                response = requests.post(API_URL,json=payload, headers=headers, timeout=60)

                if response.status_code ==  200:
                    data = response.json()
                    reply = data.get("reply","")
                    st.markdown(reply)
                    st.session_state.simple_messages.append({"role":"assistant","content":reply})

                else:
                    st.error(f"Error {response.status_code}")
                    st.code(response.text)

            except requests.exceptions.ConnectionError:
                st.error("Flask app is not running")
                