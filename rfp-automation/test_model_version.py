import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print(f"Testing access to model: gemini-2.5-flash")
try:
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content("Hello")
    print("SUCCESS: Model exists and responded.")
except Exception as e:
    print(f"FAILURE: {e}")
