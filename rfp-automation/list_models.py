"""List available Gemini models"""

import google.generativeai as genai

api_key = "AIzaSyDKQBWUy9ZHFuFE0bDjXZYhxiCmoQaCh5M"
genai.configure(api_key=api_key)

print("Available Gemini models:")
for model in genai.list_models():
    print(f"- {model.name}")
