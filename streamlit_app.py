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
            # Try to detect browser and provide appropriate guidance
            st.info("🔍 **Browser Detection:** PDF preview may be blocked by your browser.")
            
            # Create a simple preview attempt with clear fallback
            base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
            
            pdf_display = f'''
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; background: #f9f9f9;">
                <div style="margin-bottom: 15px; font-weight: bold; color: #333; font-size: 16px;">📄 {uploaded_file.name}</div>
                
                <div style="background: #fff; border: 1px solid #ccc; border-radius: 5px; padding: 20px; text-align: center;">
                    <p style="margin-bottom: 15px; color: #666;">Attempting to load PDF preview...</p>
                    
                    <object 
                        data="data:application/pdf;base64,{base64_pdf}" 
                        type="application/pdf" 
                        width="100%" 
                        height="400px"
                        style="border: 1px solid #ddd; border-radius: 3px;"
                    >
                        <div style="padding: 20px; color: #666;">
                            <p>📱 <strong>PDF Preview Not Available</strong></p>
                            <p>Your browser has blocked the PDF preview for security reasons.</p>
                            <p style="margin-top: 15px;">
                                <a href="data:application/pdf;base64,{base64_pdf}" 
                                   download="{uploaded_file.name}"
                                   style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                                    📥 Download PDF
                                </a>
                            </p>
                        </div>
                    </object>
                </div>
                
                <div style="margin-top: 15px; padding: 10px; background: #e7f3ff; border-radius: 5px; border-left: 4px solid #007bff;">
                    <p style="margin: 0; color: #0056b3;"><strong>💡 Tip:</strong> Use the "Download" tab for the best experience!</p>
                </div>
            </div>
            '''
            st.markdown(pdf_display, unsafe_allow_html=True)
            uploaded_file.seek(0)  # Reset file pointer
    
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
        st.markdown("### 🌐 Browser-Specific Instructions:")
        
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
            
            1. **Try the PDF Viewer tab** - it might work!
            2. **Download and open** if preview doesn't work
            3. **Firefox has built-in PDF viewer** - usually works well
            """)
        
        with st.expander("Edge Users"):
            st.markdown("""
            **Microsoft Edge has good PDF support:**
            
            1. **Try the PDF Viewer tab** - Edge often works
            2. **Download and open** if needed
            3. **Edge has built-in PDF viewer** - usually reliable
            """)
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions:")
        col1, col2 = st.columns(2)
        with col1:
            st.button("🔄 Try Preview Again", help="Refresh the preview tab")
        with col2:
            st.button("📋 Copy File Name", help="Copy the PDF filename to clipboard")
    
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