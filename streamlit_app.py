import streamlit as st
import requests
import base64
import google.generativeai as genai
import fitz
import tempfile
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import threading
import time

# Gemini API setup
genai.configure(api_key="AIzaSyDAWV9nONsWGIiIOCh7TzJ9xocnME994IY")
model = genai.GenerativeModel("gemini-2.0-flash")

# FastAPI app setup
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    pdf_base64: str
    question: str

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    try:
        pdf_data = base64.b64decode(request.pdf_base64)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_data)
            tmp_file_path = tmp_file.name

        doc = fitz.open(tmp_file_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        prompt = f"""
📄 PDF CONTENT:
{full_text}

❓ QUESTION:
{request.question}

📘 ANSWER:
"""

        response = model.generate_content(prompt)
        return {"answer": response.text.strip()}

    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def read_root():
    return {"message": "PDF Analyzer Backend is running!"}

# Function to start the FastAPI server
def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Start the server in a separate thread
@st.cache_resource
def start_backend():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Give the server time to start
    return server_thread

# Initialize session states
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Start the backend server
start_backend()

st.set_page_config(page_title="PDF Analyzer", page_icon="🔎", layout="wide")

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