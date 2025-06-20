from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ai_engine import generate_qa_prompt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI-Powered Interview Q&A Generator",
    description="Generate technical and HR interview questions using LLM.",
    version="1.0.0"
)

# More restrictive CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Only allow Streamlit
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only necessary methods
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Root endpoint for API health check."""
    return {"message": "Welcome to the AI-Powered Interview Q&A Generator API", "status": "healthy"}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI Q&A Generator"}

@app.get("/generate_questions")
def generate_questions(
    role: str = Query(..., description="Job role (e.g., data scientist)", min_length=1, max_length=100)
):
    """Generate interview questions for a specific role."""
    try:
        # Validate input
        role = role.strip()
        if not role:
            raise HTTPException(status_code=400, detail="Role cannot be empty")
        
        logger.info(f"Generating questions for role: {role}")
        
        output = generate_qa_prompt(role)
        
        # Validate output
        if not output or not isinstance(output, list):
            raise HTTPException(status_code=500, detail="Failed to generate valid questions")
        
        return {
            "role": role,
            "questions_and_answers": output,
            "total_questions": len(output)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)