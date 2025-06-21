import google.generativeai as genai
import os

# Load Gemini API key
api_key = os.getenv("GEMINI_API_KEY") or "your-real-api-key"
genai.configure(api_key=api_key)

print("Gemini API key loaded:", bool(api_key))

# Check all available models
print("\nAvailable models and supported methods:\n")
models = genai.list_models()
for model in models:
    print(f"{model.name} ➤ supports generateContent: {'generateContent' in model.supported_generation_methods}")
