import streamlit as st
import requests
import base64
import subprocess
import threading
import time
import os

# Set page config must be the first Streamlit command
st.set_page_config(page_title="PDF Analyzer", page_icon="🔎", layout="wide")

# Function to start the API server
def start_api_server():
    try:
        subprocess.run(["python", "api.py"], check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to start API server: {e}")

# Start the API server in a separate thread
@st.cache_resource
def start_backend():
    server_thread = threading.Thread(target=start_api_server, daemon=True)
    server_thread.start()
    time.sleep(3)  # Give the server time to start
    return server_thread

# Initialize session states
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Start the backend server
start_backend()

st.title("🖊 Analyze Your PDF")

col1, col2 = st.columns([1, 2])

with col1:
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file:
        st.markdown("#### 📑 Preview")
        base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500px" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        uploaded_file.seek(0)  # reset pointer after reading

with col2:
    if uploaded_file:
        with st.form(key="query_form"):
            question = st.text_input("❓ Ask a Follow-Up about your PDF", key="current_question")
            submit = st.form_submit_button("Ask")

        if submit and question:
            with st.spinner("🔍 Analyzing..."):
                try:
                    encoded_pdf = base64.b64encode(uploaded_file.read()).decode("utf-8")
                    response = requests.post(
                        "http://localhost:8000/analyze",
                        json={"pdf_base64": encoded_pdf, "question": question},
                        timeout=30
                    )
                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.session_state.chat_history.append((question, answer))
                        st.session_state.qa_history.append((question, answer))

                        # Reset question input
                        del st.session_state["current_question"]
                        st.rerun()
                    else:
                        st.error("❌ Backend returned an error.")
                except Exception as e:
                    st.error(f"❌ Could not reach backend: {e}")

        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### 💬 Chat History")
            for q, a in reversed(st.session_state.chat_history):
                with st.chat_message("user"):
                    st.markdown(q)
                with st.chat_message("assistant"):
                    st.markdown(a) 