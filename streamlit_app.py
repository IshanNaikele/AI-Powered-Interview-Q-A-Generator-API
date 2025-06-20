import streamlit as st
import requests
import json
import time
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
FASTAPI_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 120

# Page configuration
st.set_page_config(
    page_title="AI Q&A Generator", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .question-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .technical-question {
        border-left-color: #ff7f0e;
    }
    .hr-question {
        border-left-color: #2ca02c;
    }
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #c62828;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health() -> bool:
    """Check if FastAPI server is running."""
    try:
        response = requests.get(f"{FASTAPI_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def validate_role_input(role: str) -> tuple[bool, str]:
    """Validate the role input."""
    if not role or not role.strip():
        return False, "Role cannot be empty"
    
    if len(role.strip()) < 2:
        return False, "Role must be at least 2 characters long"
    
    if len(role.strip()) > 100:
        return False, "Role must be less than 100 characters"
    
    # Check for potentially harmful characters
    if any(char in role for char in ['<', '>', '{', '}', '[', ']']):
        return False, "Role contains invalid characters"
    
    return True, ""

def make_api_request(role: str) -> tuple[bool, Dict[str, Any], str]:
    """Make request to FastAPI and return success status, data, and error message."""
    try:
        with st.spinner("🤖 Generating questions... This may take up to 2 minutes"):
            response = requests.get(
                f"{FASTAPI_URL}/generate_questions",
                params={"role": role.strip()},
                timeout=REQUEST_TIMEOUT
            )
        
        if response.status_code == 200:
            data = response.json()
            return True, data, ""
        elif response.status_code == 400:
            error_data = response.json()
            return False, {}, error_data.get("detail", "Bad request")
        elif response.status_code == 500:
            return False, {}, "Server error occurred. Please try again."
        else:
            return False, {}, f"Unexpected error: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return False, {}, "Request timed out. The AI model might be busy. Please try again."
    
    except requests.exceptions.ConnectionError:
        return False, {}, "Cannot connect to the server. Please ensure FastAPI is running."
    
    except requests.exceptions.RequestException as e:
        return False, {}, f"Network error: {str(e)}"
    
    except json.JSONDecodeError:
        return False, {}, "Invalid response from server"
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False, {}, "An unexpected error occurred"

def display_questions(questions: List[Dict[str, Any]], role: str):
    """Display the generated questions in a formatted way."""
    st.success(f"✅ Generated {len(questions)} questions for **{role}**!")
    
    # Separate technical and HR questions
    technical_questions = [q for q in questions if q.get('type') == 'technical']
    hr_questions = [q for q in questions if q.get('type') == 'hr']
    
    # Display technical questions
    if technical_questions:
        st.subheader("🔧 Technical Questions")
        for idx, qa in enumerate(technical_questions, 1):
            with st.container():
                st.markdown(f"""
                <div class="question-card technical-question">
                    <h4>❓ Technical Q{idx}: {qa['question']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("💡 View Answer", expanded=False):
                    st.markdown(f"**Answer:** {qa['answer']}")
                
                st.markdown("---")
    
    # Display HR questions
    if hr_questions:
        st.subheader("👥 HR/Behavioral Questions")
        for idx, qa in enumerate(hr_questions, 1):
            with st.container():
                st.markdown(f"""
                <div class="question-card hr-question">
                    <h4>❓ HR Q{idx}: {qa['question']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("💡 View Answer", expanded=False):
                    st.markdown(f"**Answer:** {qa['answer']}")
                
                st.markdown("---")
    
    # Fallback for questions without type classification
    untyped_questions = [q for q in questions if 'type' not in q or q.get('type') not in ['technical', 'hr']]
    if untyped_questions:
        st.subheader("📋 All Questions")
        for idx, qa in enumerate(untyped_questions, 1):
            with st.container():
                st.markdown(f"""
                <div class="question-card">
                    <h4>❓ Q{idx}: {qa['question']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("💡 View Answer", expanded=False):
                    st.markdown(f"**Answer:** {qa['answer']}")
                
                st.markdown("---")
    
    # Download option
    if st.button("📥 Download Questions as JSON"):
        json_str = json.dumps({"role": role, "questions": questions}, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"{role.lower().replace(' ', '_')}_interview_questions.json",
            mime="application/json"
        )

def main():
    """Main application function."""
    # Header
    st.markdown('<h1 class="main-header">🧠 AI Interview Q&A Generator</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Generate realistic technical and HR interview questions for any job role using AI.
    Perfect for interview preparation or HR professionals creating interview guides.
    """)
    
    # API health check
    if not check_api_health():
        st.error("⚠️ FastAPI server is not running. Please start the server first.")
        st.code("uvicorn main:app --reload", language="bash")
        st.stop()
    
    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ About")
        st.info("""
        This tool generates:
        - 3 Technical questions
        - 2 HR/Behavioral questions
        
        Powered by Ollama + Mistral AI
        """)
        
        st.header("💡 Tips")
        st.markdown("""
        - Be specific with job roles (e.g., "Senior Python Developer" vs "Developer")
        - Try roles like: Data Scientist, Frontend Developer, Product Manager, etc.
        - Questions are generated fresh each time
        """)
    
    # Main form
    with st.form("input_form", clear_on_submit=False):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            role = st.text_input(
                "🎯 Enter a job role:",
                value="Data Scientist",
                placeholder="e.g., Senior Frontend Developer, Product Manager, DevOps Engineer",
                help="Be specific for better results"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
            submitted = st.form_submit_button("🚀 Generate Questions", use_container_width=True)
    
    # Process form submission
    if submitted:
        # Validate input
        is_valid, error_message = validate_role_input(role)
        
        if not is_valid:
            st.error(f"❌ Invalid input: {error_message}")
            return
        
        # Make API request
        success, data, error_message = make_api_request(role)
        
        if success:
            questions = data.get("questions_and_answers", [])
            
            if not questions:
                st.warning("⚠️ No questions were generated. Please try again.")
                return
            
            # Check for error indicators in questions
            if (len(questions) > 0 and 
                any(error_word in questions[0].get("question", "").lower() 
                    for error_word in ["error", "failed", "timeout", "connection"])):
                
                st.error("❌ Something went wrong on the backend:")
                st.code(questions[0].get("answer", "Unknown error"))
                return
            
            # Display questions
            display_questions(questions, role)
            
        else:
            st.markdown(f"""
            <div class="error-message">
                <strong>❌ Failed to generate questions</strong><br>
                {error_message}
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>Built with Streamlit, FastAPI, and Ollama</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()