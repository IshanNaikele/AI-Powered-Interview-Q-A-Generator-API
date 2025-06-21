import requests
from typing import List, Dict
import json
import re
import google.generativeai as genai
import os 


# Ollama settings for job roles
OLLAMA_API_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "mistral"

# Gemini settings for resume
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

def generate_prompt(role: str) -> str:
    return f"""
You are an expert interviewer.

Generate exactly 5 realistic interview questions and answers for the job role: {role}.

Make 3 technical and 2 HR-based.

Return ONLY valid JSON without any additional text or formatting. Format as:
[
    {{
        "question": "...",
        "answer": "..."
    }},
    {{
        "question": "...",
        "answer": "..."
    }},
    {{
        "question": "...",
        "answer": "..."
    }},
    {{
        "question": "...",
        "answer": "..."
    }},
    {{
        "question": "...",
        "answer": "..."
    }}
]
"""

def generate_resume_prompt(resume_text: str) -> str:
    return f"""
You are an expert technical interviewer.

Given the resume content below, generate exactly 5 interview questions and answers in strict JSON format.

Requirements:
- 3 questions must be technical based on the resume.
- 2 questions must be HR/personal questions.
- Output should be ONLY a valid JSON list of objects, with this exact structure:

[
  {{
    "question": "Your question here",
    "answer": "The answer here"
  }}
]

Resume Content:
{resume_text}

Only return the JSON list. No explanations or formatting.
"""

def extract_json_from_response(text: str) -> str:
    """Extract JSON array from response text"""
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    return text.strip()

def generate_qa_pairs(role: str) -> List[Dict[str, str]]:
    """Generate Q&A pairs for job role using Ollama"""
    prompt = generate_prompt(role)
    print(f"Generating Q&A for role: {role}")

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
            timeout=120
        )
        
        if response.status_code != 200:
            return [{"question": "API Error", "answer": f"Status code: {response.status_code}"}]

        result_text = response.json()["response"].strip()
        json_text = extract_json_from_response(result_text)
        qa_pairs = json.loads(json_text)
        
        if not isinstance(qa_pairs, list) or len(qa_pairs) != 5:
            return [{"question": "Invalid response format", "answer": "Expected 5 Q&A pairs"}]
        
        return qa_pairs

    except Exception as ex:
        return [{"question": "Error occurred", "answer": str(ex)}]

def generate_qa_pairs_from_resume(resume_text: str) -> List[Dict[str, str]]:
    """Generate Q&A pairs based on resume content using Gemini"""
    prompt = generate_resume_prompt(resume_text)
    print(f"Generating Q&A from resume using Gemini")

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        result_text = response.text.strip()
        json_text = extract_json_from_response(result_text)
        qa_pairs = json.loads(json_text)
        
        if not isinstance(qa_pairs, list) or len(qa_pairs) != 5:
            return [{"question": "Invalid response format", "answer": "Expected 5 Q&A pairs"}]
        
        return qa_pairs

    except Exception as ex:
        return [{"question": "Error occurred", "answer": str(ex)}]

# Example usage
if __name__ == "__main__":
    role = "Software Engineer"
    qa_pairs = generate_qa_pairs(role)
    
    print("\n=== GENERATED Q&A PAIRS ===")
    for i, qa in enumerate(qa_pairs, 1):
        print(f"\nQ{i}: {qa['question']}")
        print(f"A{i}: {qa['answer']}")