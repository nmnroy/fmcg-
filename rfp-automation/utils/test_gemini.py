import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print("\nTesting Gemini 2.5 Flash API...")
    response = model.generate_content("Say hello from Asian Paints RFP System")
    
    print("SUCCESS! Gemini 2.5 Flash API is working!")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {str(e)}")