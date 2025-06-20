import requests
from typing import List, Dict
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "mistral"

def generate_prompt(role: str) -> str:
    return f"""
    You are an expert interviewer.

    Generate exactly 5 realistic interview questions and answers for the job role: {role}.

    Make 3 technical and 2 HR-based.

    Format as JSON list like:
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

def generate_qa_prompt(role: str) -> List[Dict[str, str]]:
    prompt = generate_prompt(role)

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
            timeout=120
        )

        # DEBUG print
        print("=== RAW LLM RESPONSE ===")
        print(response.text)

        result_text = response.json()["response"].strip()
        return json.loads(result_text)

    except requests.exceptions.RequestException as e:
        return [{"question": "LLM request failed", "answer": str(e)}]
    except Exception as ex:
        return [{"question": "Unexpected error", "answer": str(ex)}]

