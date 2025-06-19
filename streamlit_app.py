import streamlit as st
import requests
import base64
import google.generativeai as genai
import fitz
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config must be the first Streamlit command
st.set_page_config(page_title="PDF Analyzer", page_icon="🔎", layout="wide")

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check if API key is available
if not GEMINI_API_KEY:
    st.error("""
    ❌ GEMINI_API_KEY not found! 
    
    Please set the GEMINI_API_KEY environment variable in Streamlit Cloud secrets.
    
    Get your API key from: https://makersuite.google.com/app/apikey
    """)
    st.stop()

# Gemini API setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Function to analyze PDF
def analyze_pdf(pdf_data, question):
    try:
        # Decode base64 PDF data
        pdf_bytes = base64.b64decode(pdf_data)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name

        # Extract text from PDF
        doc = fitz.open(tmp_file_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        # Create prompt
        prompt = f"""
📄 PDF CONTENT:
{full_text}

❓ QUESTION:
{question}

📘 ANSWER:
"""

        # Generate response
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"Error analyzing PDF: {str(e)}"

# Initialize session states
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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
                    # Read the uploaded file
                    uploaded_file.seek(0)
                    pdf_content = uploaded_file.read()
                    encoded_pdf = base64.b64encode(pdf_content).decode("utf-8")
                    
                    # Analyze directly without backend
                    answer = analyze_pdf(encoded_pdf, question)
                    
                    # Add to chat history
                    st.session_state.chat_history.append((question, answer))
                    st.session_state.qa_history.append((question, answer))

                    # Reset question input
                    del st.session_state["current_question"]
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")

        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### 💬 Chat History")
            for q, a in reversed(st.session_state.chat_history):
                with st.chat_message("user"):
                    st.markdown(q)
                with st.chat_message("assistant"):
                    st.markdown(a) 