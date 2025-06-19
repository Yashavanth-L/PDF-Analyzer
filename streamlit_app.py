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
        # Check file size first
        file_size = len(uploaded_file.getvalue())
        file_size_mb = file_size / (1024 * 1024)
        
        if file_size_mb > 5:  # If file is larger than 5MB
            st.warning("⚠️ File is too large for preview. Please use the Download tab.")
            st.info(f"File size: {file_size_mb:.2f} MB (max 5MB for preview)")
        else:
            # Simple, reliable approach - just show file info and download option
            st.info("🔍 **PDF Preview Status:** Browser preview may be blocked for security reasons.")
            
            # Show file details in a nice card
            st.markdown(f"""
            <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin: 10px 0;">
                <h4 style="color: #495057; margin-bottom: 15px;">📄 {uploaded_file.name}</h4>
                <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                    <span style="color: #6c757d;">📏 Size: {file_size_mb:.2f} MB</span>
                    <span style="color: #6c757d;">📄 Type: PDF</span>
                </div>
                <div style="background: #e9ecef; border-radius: 5px; padding: 15px; text-align: center;">
                    <p style="color: #495057; margin: 0;">📱 <strong>Preview not available</strong></p>
                    <p style="color: #6c757d; margin: 5px 0;">Use the Download tab to view this PDF</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.download_button(
            label="📥 Download PDF",
            data=uploaded_file.getvalue(),
            file_name=uploaded_file.name,
            mime="application/pdf",
            help="Click to download and view the PDF in your browser"
        )
        
        # Show file size info
        file_size = len(uploaded_file.getvalue())
        file_size_mb = file_size / (1024 * 1024)
        st.write(f"**File size:** {file_size_mb:.2f} MB")
        
        # Provide clear instructions for different browsers
        st.markdown("### 🌐 How to View Your PDF:")
        
        with st.expander("Chrome Users"):
            st.markdown("""
            **Chrome blocks PDF previews for security. Here's how to view your PDF:**
            
            1. **Click the Download button above** 
            2. **Choose "Open"** when prompted
            3. **Or save and open** in your default PDF viewer
            
            **Alternative:** Use Firefox or Edge for better PDF support
            """)
        
        with st.expander("Firefox Users"):
            st.markdown("""
            **Firefox has good PDF support:**
            
            1. **Download the PDF** using the button above
            2. **Firefox will open it** in its built-in PDF viewer
            3. **Or save and open** in your preferred PDF app
            """)
        
        with st.expander("Edge Users"):
            st.markdown("""
            **Microsoft Edge has good PDF support:**
            
            1. **Download the PDF** using the button above
            2. **Edge will open it** in its built-in PDF viewer
            3. **Or save and open** in your preferred PDF app
            """)
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", help="Refresh the file information"):
                st.rerun()
        with col2:
            if st.button("📋 Copy Name", help="Copy the PDF filename"):
                st.write(f"Copied: {uploaded_file.name}")
    
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
        
        # Browser compatibility info
        st.markdown("### 🌐 Browser Compatibility:")
        st.markdown("""
        | Browser | PDF Preview | Download | Recommendation |
        |---------|-------------|----------|----------------|
        | **Firefox** | ✅ Usually works | ✅ Always works | **Best choice** |
        | **Edge** | ✅ Usually works | ✅ Always works | **Good choice** |
        | **Safari** | ⚠️ Sometimes works | ✅ Always works | **Try preview** |
        | **Chrome** | ❌ Blocked | ✅ Always works | **Use download** |
        """)
        
        # File size compatibility
        st.markdown("### 📏 File Size Compatibility:")
        if file_size_mb <= 5:
            st.success("✅ File size is suitable for browser preview (≤5MB)")
        else:
            st.warning("⚠️ File is too large for browser preview (>5MB)")
            st.info("Large files work best when downloaded and opened locally.")
        
        # Tips for better experience
        st.markdown("### 💡 Tips for Better Experience:")
        st.markdown("""
        - **Use Firefox or Edge** for better PDF support
        - **Download and open** for the most reliable experience
        - **Keep files under 5MB** for better compatibility
        - **Use a PDF reader app** for large or complex documents
        """)

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