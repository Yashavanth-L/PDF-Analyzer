import streamlit as st
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

# Function to display PDF preview
def display_pdf_preview(uploaded_file):
    st.markdown("#### 📑 Preview")
    
    # Create tabs for different preview options
    tab1, tab2, tab3 = st.tabs(["📄 PDF Viewer", "📥 Download", "ℹ️ Info"])
    
    with tab1:
        try:
            # Try to use streamlit-pdf-viewer if available
            try:
                from streamlit_pdf_viewer import pdf_viewer
                pdf_viewer(uploaded_file, width=700)
            except ImportError:
                # Fallback to iframe with better error handling
                base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
                pdf_display = f'''
                <iframe 
                    src="data:application/pdf;base64,{base64_pdf}" 
                    width="100%" 
                    height="500px" 
                    type="application/pdf"
                    style="border: 1px solid #ddd; border-radius: 5px;"
                >
                    <p>Your browser doesn't support PDF preview. 
                    <a href="data:application/pdf;base64,{base64_pdf}" download="{uploaded_file.name}">Download PDF</a></p>
                </iframe>
                '''
                st.markdown(pdf_display, unsafe_allow_html=True)
                uploaded_file.seek(0)  # Reset file pointer
        except Exception as e:
            st.warning(f"PDF preview not available: {str(e)}")
            st.info("Please use the Download tab to view the PDF.")
    
    with tab2:
        st.download_button(
            label="📥 Download PDF",
            data=uploaded_file.getvalue(),
            file_name=uploaded_file.name,
            mime="application/pdf",
            help="Click to download and view the PDF in your browser"
        )
        st.info("💡 **Tip:** Download the PDF to view it properly in your browser.")
    
    with tab3:
        file_size = len(uploaded_file.getvalue())
        file_size_mb = file_size / (1024 * 1024)
        
        st.write(f"**File Name:** {uploaded_file.name}")
        st.write(f"**File Size:** {file_size_mb:.2f} MB")
        st.write(f"**File Type:** PDF")
        
        # Try to get page count
        try:
            uploaded_file.seek(0)
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            page_count = len(doc)
            st.write(f"**Pages:** {page_count}")
            doc.close()
            uploaded_file.seek(0)
        except:
            st.write("**Pages:** Unable to determine")

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
        display_pdf_preview(uploaded_file)

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