"""Direct test of Gemini API with hardcoded key"""

import google.generativeai as genai
import time

# Use the API key directly
api_keys = [
    "AIzaSyBKV1AJMbit5K8-G_p7pZD4T_crmWgDjvI",
    "AIzaSyCRN0kdEv7Ug4msqchWEzgAcQkcnk0HYuM"
]

print("🧪 Testing Gemini API Keys...")

models_to_try = ["gemini-1.5-flash", "gemini-pro", "gemini-1.5-pro"]

for i, api_key in enumerate(api_keys):
    masked_key = f"{api_key[:5]}...{api_key[-5:]}"
    print(f"\n[{i+1}/{len(api_keys)}] Testing Key: {masked_key}")
    
    success = False
    for model_name in models_to_try:
        if success: break
        print(f"   Trying model: {model_name}...")
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name) 
            response = model.generate_content("Reply with just: API KEY WORKS")
            
            print(f"   📨 Response: {response.text}")
            print(f"   ✅ SUCCESS with {model_name}")
            success = True
            
        except Exception as e:
            print(f"   ❌ ERROR with {model_name}: {str(e)}")
            
    if not success:
        print("   ⛔ FAILED all models with this key.")
    
    time.sleep(1) # Brief pause
