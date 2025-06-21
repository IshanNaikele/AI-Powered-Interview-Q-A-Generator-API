from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ai_engine import generate_qa_pairs  # Fixed import name
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI-Powered Interview Q&A Generator",
    description="Generate technical and HR interview questions using LLM.",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Allow Streamlit
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Root endpoint for API health check."""
    return {
        "message": "Welcome to the AI-Powered Interview Q&A Generator API", 
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI Q&A Generator"}

@app.get("/generate_questions")
def generate_questions(
    role: str = Query(
        ..., 
        description="Job role (e.g., Software Engineer, Data Scientist)", 
        min_length=1, 
        max_length=100,
        example="Software Engineer"
    )
):
    """
    Generate 5 interview questions (3 technical + 2 HR) for a specific job role.
    
    Returns:
        - role: The job role requested
        - questions_and_answers: List of Q&A pairs
        - total_questions: Number of questions generated
    """
    try:
        # Validate and clean input
        role = role.strip()
        if not role:
            raise HTTPException(status_code=400, detail="Role cannot be empty")
        
        if len(role) < 2:
            raise HTTPException(status_code=400, detail="Role must be at least 2 characters long")
        
        logger.info(f"Generating questions for role: {role}")
        
        # Generate Q&A pairs
        qa_pairs = generate_qa_pairs(role)  # Fixed function name
        
        # Validate output
        if not qa_pairs or not isinstance(qa_pairs, list):
            logger.error(f"Invalid output from generate_qa_pairs: {qa_pairs}")
            raise HTTPException(status_code=500, detail="Failed to generate valid questions")
        
        # Check if any error responses were returned
        if len(qa_pairs) == 1 and "error" in qa_pairs[0].get("question", "").lower():
            logger.error(f"AI engine returned error: {qa_pairs[0]}")
            raise HTTPException(status_code=500, detail=f"AI generation failed: {qa_pairs[0]['answer']}")
        
        logger.info(f"Successfully generated {len(qa_pairs)} questions for {role}")
        
        return {
            "role": role,
            "questions_and_answers": qa_pairs,
            "total_questions": len(qa_pairs),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating questions for role '{role}': {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return {"detail": "Endpoint not found", "available_endpoints": ["/", "/health", "/generate_questions"]}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")