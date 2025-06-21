# 🎯 AI-Powered Interview Q&A Generator

> Generate customized interview questions and answers using AI - powered by Ollama and Google Gemini

## 📋 Overview

An intelligent interview preparation tool that generates realistic technical and HR interview questions based on either a **job role** or **uploaded resume**. The system uses different AI models optimized for each input type to ensure relevant and high-quality questions.

## ✨ Features

- **Dual Input Modes**: Generate questions from job role or resume upload
- **Smart AI Selection**: Uses Ollama (Mistral) for role-based questions, Google Gemini for resume analysis
- **Multiple File Support**: PDF, DOCX, and TXT resume formats
- **Structured Output**: Always generates 5 questions (3 technical + 2 HR)
- **Clean API**: RESTful FastAPI backend with proper error handling
- **User-Friendly Interface**: Simple Streamlit web interface
- **Robust File Processing**: Handles multiple text encodings and file types

## 🔧 Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **Ollama** - Local LLM for job role questions (Mistral model)
- **Google Gemini API** - Advanced AI for resume-based questions
- **PyPDF2** - PDF text extraction
- **python-docx** - DOCX file processing

### Frontend
- **Streamlit** - Interactive web interface

### File Processing
- **PyPDF2** - PDF parsing
- **python-docx** - Microsoft Word document handling
- **Built-in encoding support** - UTF-8, Latin-1, ISO-8859-1, CP1252

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running locally
3. **Google Gemini API key** (free tier available)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/interview-qa-generator.git
cd interview-qa-generator
```

2. **Install dependencies**
```bash
pip install fastapi uvicorn streamlit
pip install google-generativeai requests
pip install PyPDF2 python-docx
```

3. **Set up Ollama**
```bash
# Install Ollama (visit https://ollama.ai for instructions)
ollama pull mistral
ollama serve
```

4. **Configure Gemini API**
```bash
# Set your Gemini API key as environment variable
export GEMINI_API_KEY="your-api-key-here"
```

### Running the Application

1. **Start the FastAPI backend**
```bash
python main.py
# Server runs on http://localhost:8000
```

2. **Launch the Streamlit frontend** (new terminal)
```bash
streamlit run frontend.py
# Interface opens at http://localhost:8501
```

## 📚 API Documentation

### Endpoints

#### `GET /`
Health check and API information

#### `GET /health`
Service health status

#### `GET /generate_questions`
Generate questions from job role
- **Parameter**: `role` (string) - Job title/role
- **Returns**: 5 Q&A pairs (3 technical + 2 HR)

#### `POST /generate_questions_from_resume`
Generate questions from uploaded resume
- **Body**: Multipart form data with resume file
- **Supported formats**: PDF, DOCX, TXT
- **Returns**: 5 personalized Q&A pairs

### Example API Usage

```python
import requests

# Generate questions for a role
response = requests.get(
    "http://localhost:8000/generate_questions",
    params={"role": "Software Engineer"}
)

# Upload resume for personalized questions
with open("resume.pdf", "rb") as f:
    files = {"file": ("resume.pdf", f, "application/pdf")}
    response = requests.post(
        "http://localhost:8000/generate_questions_from_resume",
        files=files
    )
```

## 🏗️ Project Structure

```
interview-qa-generator/
├── main.py                 # FastAPI application
├── ai_engine.py           # AI model integration
├── resume_parser.py       # File processing utilities
├── frontend.py            # Streamlit interface
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## 🔄 How It Works

### Job Role Flow
1. User enters job role (e.g., "Data Scientist")
2. System sends prompt to Ollama (Mistral model)
3. AI generates 5 relevant questions with answers
4. JSON response parsed and returned

### Resume Upload Flow
1. User uploads resume file (PDF/DOCX/TXT)
2. System extracts text using appropriate parser
3. Resume content sent to Google Gemini
4. AI analyzes resume and generates personalized questions
5. Structured response returned to user

## 📊 Sample Output

```json
{
  "role": "Software Engineer",
  "questions_and_answers": [
    {
      "question": "Explain the difference between SQL and NoSQL databases",
      "answer": "SQL databases are relational with fixed schemas..."
    },
    {
      "question": "How do you handle version control in team projects?",
      "answer": "I use Git for version control with branching strategies..."
    }
  ],
  "total_questions": 5,
  "status": "success"
}
```

## ⚙️ Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your-gemini-api-key
OLLAMA_API_URL=http://localhost:11434/api/generate  # Default
LLM_MODEL=mistral  # Ollama model name
```

### Customization Options
- **Question Count**: Modify the prompt to generate different numbers of questions
- **Question Types**: Adjust technical/HR ratio in prompts
- **AI Models**: Switch Ollama models or use different Gemini variants
- **File Support**: Add support for additional file formats

## 🚨 Error Handling

The system includes comprehensive error handling for:
- Invalid file formats
- Empty or corrupted files
- AI model failures
- Network connectivity issues
- Malformed AI responses

## 🔒 Security Considerations

- File upload size limits enforced
- Input validation on all endpoints
- CORS configured for specific origins
- No sensitive data stored locally

## 📈 Performance Notes

- **Ollama**: Requires local resources, good for privacy
- **Gemini**: Cloud-based, faster but requires internet
- **File Processing**: In-memory processing, suitable for typical resume sizes
- **Concurrent Users**: Limited by Ollama local instance

## 🔄 Future Enhancements

- [ ] Question difficulty levels
- [ ] Industry-specific templates
- [ ] Question quality scoring
- [ ] User feedback integration
- [ ] Interview simulation mode
- [ ] Export to PDF/Word
- [ ] Multi-language support

## 🐛 Troubleshooting

### Common Issues

**Ollama Connection Error**
```bash
# Ensure Ollama is running
ollama serve
ollama list  # Check installed models
```

**Gemini API Error**
```bash
# Verify API key is set
echo $GEMINI_API_KEY
```

**File Upload Issues**
- Check file size (<10MB recommended)
- Ensure file is not password-protected
- Try different file format

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [Ishan Naikele](https://github.com/IshanNaikele)
- LinkedIn: [Ishan Naikele](https://www.linkedin.com/in/ishan-naikele-b759562b0/)
- Email: ishannaikele23@gmail.com

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for local LLM infrastructure
- [Google Gemini](https://ai.google.dev) for advanced AI capabilities
- [FastAPI](https://fastapi.tiangolo.com) for the excellent web framework
- [Streamlit](https://streamlit.io) for rapid UI development

---

⭐ **Star this repository if you found it helpful!**
