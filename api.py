from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
import base64
import fitz
import tempfile
from fastapi.middleware.cors import CORSMiddleware

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 