from docx import Document
from PyPDF2 import PdfReader
import logging

# Logger setup
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file):
    """Extract text from a PDF file using PyPDF2."""
    try:
        pdf_reader = PdfReader(file)
        text = ''.join([page.extract_text() or '' for page in pdf_reader.pages])
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}")
        return ""

def extract_text_from_docx(file):
    """Extract text from a DOCX file using python-docx."""
    try:
        doc = Document(file)
        text = '\n'.join(para.text for para in doc.paragraphs)
        return text.strip()
    except Exception as e:
        logger.error(f"DOCX extraction error: {str(e)}")
        return ""

def extract_text_from_txt(file):
    """
    Extract text from a TXT file. Supports multiple encodings for robustness.
    """
    try:
        file_bytes = file.read()

        # Try UTF-8 first
        try:
            return file_bytes.decode('utf-8').strip()
        except UnicodeDecodeError:
            # Try fallback encodings
            for encoding in ['latin-1', 'iso-8859-1', 'cp1252']:
                try:
                    return file_bytes.decode(encoding).strip()
                except UnicodeDecodeError:
                    continue
            # Fallback to utf-8 with replacement
            return file_bytes.decode('utf-8', errors='replace').strip()

    except Exception as e:
        logger.error(f"TXT extraction error: {str(e)}")
        return ""

def extract_resume_text(uploaded_file, filename: str) -> str:
    """Main function to extract text from resume file"""
    if not uploaded_file or not filename:
        return ""

    file_extension = filename.split('.')[-1].lower()

    if file_extension == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_extension == 'docx':
        return extract_text_from_docx(uploaded_file)
    elif file_extension == 'txt':
        return extract_text_from_txt(uploaded_file)
    else:
        print(f"Unsupported file type: {file_extension}")
        return ""
