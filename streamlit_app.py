# importing the required Library 
import streamlit as st
import requests
from fpdf import FPDF
import io


# The URL in which the website will run 
API_URL = "http://localhost:8000"

# It will be shown as a heading 
st.title("🎯 Interview Q&A Generator")

#  Take Input:Either Job Role or Resume Upload 

option = st.radio("Choose input type:", ["Job Role", "Resume Upload","Both Job Role + Resume"])


def generate_pdf(qa_list, title="Interview Q&A"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", '', 12)
    for i, qa in enumerate(qa_list, 1):
        pdf.multi_cell(0, 10, f"Q{i}: {qa['question']}")
        pdf.multi_cell(0, 10, f"A{i}: {qa['answer']}")
        pdf.ln(5)
    # Output to memory buffer
    buffer = io.BytesIO()
    pdf_string = pdf.output(dest='S')
    buffer.write(pdf_string.encode('latin-1'))
    buffer.seek(0)
    return buffer
     


# If option is selected as Job Role then the if code will run 
if option == "Both Job Role + Resume":
    role = st.text_input("Enter job role:", placeholder="e.g., Data Analyst")
    uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx', 'txt'])

    if st.button("Generate Questions"):
        if role and uploaded_file:
            with st.spinner("Generating questions..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(
                        f"{API_URL}/generate_questions_from_job_and_resume",
                        params={"role": role},
                        files=files
                    )

                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Generated {data['total_questions']} questions for {data['filename']}")

                        for i, qa in enumerate(data['questions_and_answers'], 1):
                            st.subheader(f"Q{i}: {qa['question']}")
                            st.write(f"**Answer:** {qa['answer']}")
                            st.divider()

                        # ✅ Download Q&A as PDF
                        pdf_buffer = generate_pdf(data['questions_and_answers'])
                        st.download_button(
                            label="📥 Download Q&A as PDF",
                            data=pdf_buffer.getvalue(),
                            file_name="qa_pairs.pdf",
                            mime="application/pdf"
                        )

                    else:
                        try:
                            err_msg = response.json().get('detail', 'Unknown error')
                        except Exception:
                            err_msg = response.text
                        st.error(f"Error: {err_msg}")

                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
        else:
            st.warning("Please provide both job role and resume.")

elif option == "Job Role":
    # It will Take the Job Role as input (It can be Software Developer,Software Engineer ,etc)
    role = st.text_input("Enter job role:", placeholder="e.g., Software Engineer")
    
    # It will show a button as Generrating Question 
    if st.button("Generate Questions"):
        #When the role is given it wil run
        if role:
            # st.spinner used to shows a Buffer (Like youtube shows when Data Connection is slow )

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

                        # ✅ Download Q&A as PDF
                        pdf_buffer = generate_pdf(data['questions_and_answers'])
                        st.download_button(
                            label="📥 Download Q&A as PDF",
                            data=pdf_buffer.getvalue(),
                            file_name="qa_pairs.pdf",
                            mime="application/pdf"
                        )

                    else:
                        try:
                            err_msg = response.json().get('detail', 'Unknown error')
                        except Exception:
                            err_msg = response.text
                        st.error(f"Error: {err_msg}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
        # without giving role ,if user enters then it will give warning
        else:
            st.warning("Please enter a job role.")

# If option is selected as Resume Upload then else block will run 
else:  
    # It will take resume input  
    uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx', 'txt'])
    
    # same as above 
    if st.button("Generate Questions"):
        
        if uploaded_file:
            with st.spinner("Processing resume..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_URL}/generate_questions_from_resume", files=files)

                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Generated {data['total_questions']} questions from {data['filename']}")
                        
                        for i, qa in enumerate(data['questions_and_answers'], 1):
                            st.subheader(f"Q{i}: {qa['question']}")
                            st.write(f"**Answer:** {qa['answer']}")  
                            st.divider()
                        # ✅ Download Q&A as PDF
                        pdf_buffer = generate_pdf(data['questions_and_answers'])
                        st.download_button(
                            label="📥 Download Q&A as PDF",
                            data=pdf_buffer.getvalue(),
                            file_name="qa_pairs.pdf",
                            mime="application/pdf"
                        )

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
