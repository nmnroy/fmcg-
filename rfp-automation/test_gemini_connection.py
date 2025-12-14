"""Test script to verify Google Gemini API connection"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini():
    print("🧪 Testing Gemini API Key...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        
        print("🔗 Connecting to Gemini...")
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Reply with just: API KEY WORKS")
        
        print(f"📨 Response: {response.text}")
        print("✅ SUCCESS: Your Gemini API key is working!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_gemini()
