import streamlit as st
import requests
import json
import time

# Configure the page
st.set_page_config(
    page_title="AI Interview Q&A Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

@st.cache_data(ttl=300)  # Cache for 5 minutes
def call_api(role: str):
    """Call the FastAPI backend to generate questions."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/generate_questions",
            params={"role": role},
            timeout=120
        )
        
        if response.status_code == 400:
            st.error("❌ Invalid input: Please check your job role input")
            return None
        elif response.status_code == 500:
            st.error("❌ Server error: The AI service is having issues. Please try again.")
            return None
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. The AI is taking too long to respond. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Connection error: Cannot connect to the API. Make sure the server is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"🚨 API Error: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("📄 Invalid response format from server")
        return None
    except Exception as e:
        st.error(f"💥 Unexpected error: {str(e)}")
        return None

def check_api_health():
    """Check if the API is healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def display_questions(qa_pairs, role):
    """Display questions and answers in an organized format."""
    st.subheader("📋 Interview Questions & Answers")
    
    # Separate technical and HR questions
    technical_questions = []
    hr_questions = []
    
    for i, qa in enumerate(qa_pairs):
        question_lower = qa['question'].lower()
        if any(tech_word in question_lower for tech_word in 
               ['algorithm', 'code', 'programming', 'technical', 'system', 'architecture', 'database', 'api']):
            technical_questions.append((i+1, qa))
        else:
            hr_questions.append((i+1, qa))
    
    # Display technical questions
    if technical_questions:
        st.markdown("### 🔧 Technical Questions")
        for orig_num, qa in technical_questions:
            with st.expander(f"Q{orig_num}: {qa['question'][:100]}{'...' if len(qa['question']) > 100 else ''}"):
                st.markdown(f"**❓ Question:** {qa['question']}")
                st.markdown(f"**💡 Answer:** {qa['answer']}")
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"📋 Copy", key=f"copy_tech_{orig_num}"):
                        st.code(f"Q: {qa['question']}\n\nA: {qa['answer']}", language="text")
    
    # Display HR questions
    if hr_questions:
        st.markdown("### 👥 HR/Behavioral Questions")
        for orig_num, qa in hr_questions:
            with st.expander(f"Q{orig_num}: {qa['question'][:100]}{'...' if len(qa['question']) > 100 else ''}"):
                st.markdown(f"**❓ Question:** {qa['question']}")
                st.markdown(f"**💡 Answer:** {qa['answer']}")
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"📋 Copy", key=f"copy_hr_{orig_num}"):
                        st.code(f"Q: {qa['question']}\n\nA: {qa['answer']}", language="text")
    
    # Export all questions
    st.markdown("### 📤 Export Options")
    col1, col2 = st.columns(2)
    
    with col1:
        # Create downloadable text file
        qa_text = f"Interview Questions for: {role}\n{'='*50}\n\n"
        for i, qa in enumerate(qa_pairs, 1):
            qa_text += f"Question {i}: {qa['question']}\n"
            qa_text += f"Answer {i}: {qa['answer']}\n\n"
        
        st.download_button(
            label="📥 Download as Text",
            data=qa_text,
            file_name=f"interview_qa_{role.replace(' ', '_').lower()}.txt",
            mime="text/plain"
        )
    
    with col2:
        # Create downloadable JSON file
        json_data = {
            "role": role,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "questions_and_answers": qa_pairs
        }
        
        st.download_button(
            label="📥 Download as JSON",
            data=json.dumps(json_data, indent=2),
            file_name=f"interview_qa_{role.replace(' ', '_').lower()}.json",
            mime="application/json"
        )

def main():
    st.title("🤖 AI-Powered Interview Q&A Generator")
    st.markdown("Generate realistic technical and HR interview questions for any job role using AI.")
    
    # Check API health first
    is_healthy, health_data = check_api_health()
    if not is_healthy:
        st.error("🚨 **API Service Unavailable**: Please ensure the FastAPI server is running on port 8000")
        st.stop()
    
    # Input section
    st.subheader("📝 Enter Job Role")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        role = st.text_input(
            "Job Role",
            placeholder="e.g., Data Scientist, Software Engineer, Product Manager",
            help="Enter the job role you want to generate interview questions for",
            max_chars=100
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        generate_button = st.button("🚀 Generate Questions", type="primary", use_container_width=True)
    
    # Sample roles for quick selection
    st.markdown("**💡 Quick Select:**")
    sample_roles = ["Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer", "Frontend Developer"]
    selected_sample = st.selectbox("Choose a sample role:", [""] + sample_roles, key="sample_role")
    
    if selected_sample and selected_sample != role:
        st.rerun()
    
    # Use selected sample role if chosen
    if selected_sample and selected_sample != "":
        role = selected_sample
    
    # Generate button logic
    if generate_button or selected_sample:
        if not role or not role.strip():
            st.warning("⚠️ Please enter a job role first!")
            return
        
        if len(role.strip()) < 2:
            st.warning("⚠️ Job role must be at least 2 characters long!")
            return
        
        # Show loading spinner
        with st.spinner("🔄 Generating interview questions... This may take a moment."):
            result = call_api(role.strip())
        
        if result and result.get('status') == 'success':
            # Display success message
            st.success(f"✅ Successfully generated {result['total_questions']} questions for: **{result['role']}**")
            
            # Display questions and answers
            display_questions(result['questions_and_answers'], result['role'])
            
        elif result:
            st.error("❌ Failed to generate questions. Please try again.")
    
    # Sidebar with info
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This app generates realistic interview questions using AI:
        
        - **🔧 3 Technical Questions**: Role-specific technical challenges
        - **👥 2 HR Questions**: Behavioral and situational questions
        
        **📋 How to use:**
        1. Enter a job role or select from samples
        2. Click 'Generate Questions'
        3. Review the generated Q&A pairs
        4. Export as text or JSON if needed
        """)
        
        st.header("🔧 API Status")
        if is_healthy:
            st.success("✅ API Connected")
            if health_data:
                st.json(health_data)
        else:
            st.error("❌ API Offline")
            st.markdown("Make sure the FastAPI server is running on port 8000")
        
        st.header("🎯 Tips")
        st.markdown("""
        **For better results:**
        - Be specific with job roles
        - Use standard job titles
        - Try roles like: "Senior Python Developer", "ML Engineer", "Scrum Master"
        """)

if __name__ == "__main__":
    main()