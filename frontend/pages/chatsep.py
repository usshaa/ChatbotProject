import streamlit as st
import requests

API_URL = "http://localhost:5000/chat/session"

st.set_page_config(
    page_title="Chatbot",
    page_icon="https://img.icons8.com/?size=100&id=aIYDmrSk6X13&format=png&color=000000",
    layout="wide"
)

st.title("Session stateless chatbot")

if "Session_id" not in st.session_state:
    st.session_state.Session_id = None

if "Session_messages" not in st.session_state:
    st.session_state.Session_messages = []

with st.sidebar:
    st.header("Session controls")
    if st.session_state.Session_id:
        st.success(f"Active session:`{st.session_state.Session_id}`")
    else:
        st.info("No active session. The server will assign once first message start")
    
    system_prompt = st.text_area(
        "System Instruction",
        value="You are a helpful AI assistant",
        height=80
    )
    max_tokens = st.slider("Max New Tokens",min_value=16, max_value=256, value=100, step=16)
    temperature = st.slider("Temperature",min_value=0.0, max_value=1.0, value=0.7, step=0.1)

    if st.button("Start New Session",use_container_width=True):
        st.session_state.Session_id = None
        st.session_state.Session_messages = []
        st.rerun()


for msg in st.session_state.Session_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Enter your message")

if user_input:
    st.session_state.Session_messages.append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Session Processing"):
            try:
                payload = {
                    "message":user_input,
                    "system_prompt":system_prompt,
                    "max_tokens":max_tokens,
                    "temperature": temperature
                }

                if st.session_state.Session_id:
                    payload["session_id"] = st.session_state.Session_id

                headers = {"Content-Type":"application/json"}

                response = requests.post(API_URL,json=payload, headers=headers, timeout=60)

                if response.status_code ==  200:
                    data = response.json()
                    reply = data.get("reply","")
                    st.session_state.Session_id = data.get("session_id")
                    st.markdown(reply)
                    st.session_state.Session_messages.append({"role":"assistant","content":reply})

                else:
                    st.error(f"Error {response.status_code}")
                    st.code(response.text)

            except requests.exceptions.ConnectionError:
                st.error("Flask app is not running")
                