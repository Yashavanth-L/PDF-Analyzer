# PDF Analyzer

A powerful PDF analysis tool that uses Google's Gemini AI to answer questions about uploaded PDF documents. Built with Streamlit for easy deployment.

## Features

- 📄 Upload and preview PDF files
- 🤖 AI-powered question answering using Google Gemini
- 💬 Interactive chat interface
- 📱 Responsive design
- 🔄 Real-time analysis
- ☁️ Streamlit Cloud ready
- 🔐 Secure API key management

## How it Works

1. **Upload a PDF**: Users can upload any PDF file through the web interface
2. **Preview**: The PDF is displayed for review
3. **Ask Questions**: Users can ask specific questions about the PDF content
4. **AI Analysis**: The system extracts text from the PDF and uses Gemini AI to provide intelligent answers
5. **Chat History**: All Q&A interactions are saved and displayed in a chat format

## Technology Stack

- **Frontend & Backend**: Streamlit (unified)
- **AI**: Google Gemini 2.0 Flash
- **PDF Processing**: PyMuPDF (fitz)
- **Deployment**: Streamlit Cloud

## Project Structure

```
pdf-analyzer/
├── streamlit_app.py    # Main Streamlit application (frontend + backend)
├── api.py             # FastAPI backend (for local development)
├── requirements.txt   # Python dependencies
├── README.md         # Project documentation
├── .gitignore        # Git ignore file
└── env_example.txt   # Environment variables example
```

## Local Development

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd pdf-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Google Gemini API key:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file in the project root:
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
   ```
   - Replace `your_actual_api_key_here` with your real API key
   - **Important**: The `.env` file is already in `.gitignore` and will not be pushed to GitHub

4. Run the application:
```bash
streamlit run streamlit_app.py
```

The app will be available at `http://localhost:8501`

### Alternative: Separate Backend (Local Development)

If you want to run with a separate backend for development:

```bash
# Terminal 1: Start the API server
python api.py

# Terminal 2: Start the frontend (modify streamlit_app.py to use localhost:8000)
streamlit run streamlit_app.py
```

## Deployment on Streamlit Cloud

1. **Push to GitHub**: 
   - Create a new repository on GitHub
   - Push your code to the repository
   - **Note**: Your API key in `.env` will NOT be pushed to GitHub

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository
   - Set the main file path to: `streamlit_app.py`
   - Click "Deploy"

3. **Set Environment Variables in Streamlit Cloud**:
   - In Streamlit Cloud, go to your app settings
   - Click on "Secrets" in the sidebar
   - Add your API key:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```
   - Save and redeploy your app

## Security Notes

- ✅ API key is stored in environment variables
- ✅ `.env` file is ignored by git
- ✅ No sensitive data in the repository
- ✅ Secure deployment on Streamlit Cloud
- ✅ Single-file deployment eliminates backend connection issues

## File Descriptions

### `streamlit_app.py`
- Main Streamlit application (unified frontend + backend)
- Handles file uploads and user interface
- Directly processes PDFs and calls Gemini AI
- Manages chat history and session state
- **Streamlit Cloud compatible**

### `api.py`
- FastAPI backend server (for local development)
- Handles PDF processing and AI analysis
- Integrates with Google Gemini API
- Provides REST API endpoints
- **Optional for local development**

### `env_example.txt`
- Example environment variables file
- Shows what variables need to be set
- Safe to commit to repository

## API Endpoints (Local Development Only)

When using `api.py`:
- `POST /analyze`: Analyze PDF content and answer questions
- `GET /`: Health check endpoint

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

If you encounter any issues or have questions, please open an issue on GitHub. 