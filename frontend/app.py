import streamlit as st
import requests

API_BASE_URL = "http://localhost:5000"

st.set_page_config(
    page_title="Chatbot",
    page_icon="https://img.icons8.com/?size=100&id=aIYDmrSk6X13&format=png&color=000000",
    layout="wide"
)

st.title("Chatbot Dashboard")
if st.button("Check the home path (GET /)",use_container_width=False):
    try:
        res = requests.get(f"{API_BASE_URL}/",timeout=5)
        if res.status_code == 200:
            st.success(f"Backend connected: `{res.json()}`")
        else:
            st.error(f"HTTP {res.status_code}: {res.text}")
    except requests.exceptions.ConnectionError:
        st.error("Flask app is not running")