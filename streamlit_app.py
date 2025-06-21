import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("🎯 Interview Q&A Generator")

# Input options
option = st.radio("Choose input type:", ["Job Role", "Resume Upload"])

if option == "Job Role":
    role = st.text_input("Enter job role:", placeholder="e.g., Software Engineer")
    
    if st.button("Generate Questions"):
        if role:
            with st.spinner("Generating questions..."):
                try:
                    response = requests.get(f"{API_URL}/generate_questions", params={"role": role})
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Generated {data['total_questions']} questions for {data['role']}")
                        
                        for i, qa in enumerate(data['questions_and_answers'], 1):
                            st.subheader(f"Q{i}: {qa['question']}")
                            st.write(f"**Answer:** {qa['answer']}")
                            st.divider()
                    else:
                        try:
                            err_msg = response.json().get('detail', 'Unknown error')
                        except Exception:
                            err_msg = response.text
                        st.error(f"Error: {err_msg}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
        else:
            st.warning("Please enter a job role.")

else:  # Resume Upload
    uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx', 'txt'])
    
    if st.button("Generate Questions"):
        if uploaded_file:
            with st.spinner("Processing resume..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    response = requests.post(f"{API_URL}/generate_questions_from_resume", files=files)

                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Generated {data['total_questions']} questions from {data['filename']}")
                        
                        for i, qa in enumerate(data['questions_and_answers'], 1):
                            st.subheader(f"Q{i}: {qa['question']}")
                            st.write(f"**Answer:** {qa['answer']}")  
                            st.divider()
                    else:
                        try:
                            err_msg = response.json().get('detail', 'Unknown error')
                        except Exception:
                            err_msg = response.text
                        st.error(f"Error: {err_msg}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
        else:
            st.warning("Please upload a resume.")
