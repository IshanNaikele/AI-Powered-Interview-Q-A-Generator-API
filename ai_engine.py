import requests
from typing import List, Dict
import json
import re

OLLAMA_API_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "mistral"

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

def extract_json_from_response(text: str) -> str:
    """Extract JSON array from LLM response text"""
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Find JSON array pattern
    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    return text.strip()

def generate_qa_pairs(role: str) -> List[Dict[str, str]]:
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

        # DEBUG print
        print("=== RAW LLM RESPONSE ===")
        print(response.text)
        print("========================")

        result_text = response.json()["response"].strip()
        
        # Extract and clean JSON
        json_text = extract_json_from_response(result_text)
        
        # Parse JSON
        qa_pairs = json.loads(json_text)
        
        # Validate structure
        if not isinstance(qa_pairs, list) or len(qa_pairs) != 5:
            return [{"question": "Invalid response format", "answer": "Expected 5 Q&A pairs"}]
        
        return qa_pairs

    except requests.exceptions.RequestException as e:
        return [{"question": "LLM request failed", "answer": str(e)}]
    except json.JSONDecodeError as e:
        return [{"question": "JSON parsing failed", "answer": f"Invalid JSON: {str(e)}"}]
    except KeyError as e:
        return [{"question": "Response format error", "answer": f"Missing key: {str(e)}"}]
    except Exception as ex:
        return [{"question": "Unexpected error", "answer": str(ex)}]

# Example usage
if __name__ == "__main__":
    role = "Software Engineer"
    qa_pairs = generate_qa_pairs(role)
    
    print("\n=== GENERATED Q&A PAIRS ===")
    for i, qa in enumerate(qa_pairs, 1):
        print(f"\nQ{i}: {qa['question']}")
        print(f"A{i}: {qa['answer']}")