from fastapi import FastAPI, Query, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ai_engine import generate_qa_pairs, generate_qa_pairs_from_resume
from resume_parser import extract_resume_text
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
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit frontend
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
    """Basic health check endpoint."""
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
    Generate 5 interview questions (3 technical + 2 HR) for a given job role.
    """
    try:
        role = role.strip()
        if not role:
            raise HTTPException(status_code=400, detail="Role cannot be empty")
        if len(role) < 2:
            raise HTTPException(status_code=400, detail="Role must be at least 2 characters long")

        logger.info(f"Generating questions for role: {role}")
        qa_pairs = generate_qa_pairs(role)

        if not qa_pairs or not isinstance(qa_pairs, list):
            logger.error(f"Invalid output from generate_qa_pairs: {qa_pairs}")
            raise HTTPException(status_code=500, detail="Failed to generate valid questions")

        if len(qa_pairs) == 1 and "error" in qa_pairs[0].get("question", "").lower():
            logger.error(f"AI engine returned error: {qa_pairs[0]}")
            raise HTTPException(status_code=500, detail=f"AI generation failed: {qa_pairs[0]['answer']}")

        logger.info(f"Successfully generated {len(qa_pairs)} questions for {role}")

        return {
            "role": role,
            "questions_and_answers": qa_pairs,
            "total_questions": len(qa_pairs),
            "status": "success",
            "type": "role_based"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating questions for role '{role}': {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@app.post("/generate_questions_from_resume")
async def generate_questions_from_resume(file: UploadFile = File(...)):
    """
    Generate 5 interview questions (3 technical + 2 HR) from an uploaded resume.
    Supports PDF, DOCX, and TXT formats.
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")

        file_extension = file.filename.split('.')[-1].lower()
        allowed_extensions = ['pdf', 'docx', 'txt']

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )

        logger.info(f"Processing resume file: {file.filename}")
        resume_text = extract_resume_text(file.file, file.filename)

        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Resume text is too short or empty. Please upload a valid resume."
            )

        logger.info(f"Extracted {len(resume_text)} characters from resume")
        qa_pairs = generate_qa_pairs_from_resume(resume_text)

        if not qa_pairs or not isinstance(qa_pairs, list):
            logger.error(f"Invalid output from resume generation: {qa_pairs}")
            raise HTTPException(status_code=500, detail="Failed to generate valid questions from resume")

        if len(qa_pairs) == 1 and "error" in qa_pairs[0].get("question", "").lower():
            logger.error(f"AI engine returned error: {qa_pairs[0]}")
            raise HTTPException(status_code=500, detail=f"AI generation failed: {qa_pairs[0]['answer']}")

        logger.info(f"Successfully generated {len(qa_pairs)} questions from resume")

        return {
            "filename": file.filename,
            "questions_and_answers": qa_pairs,
            "total_questions": len(qa_pairs),
            "status": "success",
            "type": "resume_based"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing resume '{file.filename}': {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom handler for 404 Not Found."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint not found",
            "available_endpoints": [
                "/",
                "/health",
                "/generate_questions",
                "/generate_questions_from_resume"
            ]
        }
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
