import sys
import os
import google.generativeai as genai

sys.path.append(os.path.join(os.getcwd(), 'rfp-automation'))

try:
    from utils.api_key_manager import APIKeyManager
    
    print("Initializing API Key Manager...")
    km = APIKeyManager()
    
    print(f"\nKeys Loaded: {len(km.api_keys)}")
    
    for i, key in enumerate(km.api_keys):
        masked = f"{key[:5]}...{key[-5:]}" if key and len(key)>10 else "INVALID"
        print(f"Key {i+1}: {masked}")
        
    print("\nAttempting dry run with first key...")
    key = km.get_next_key()
    
    if not key or not key.strip():
        print("CRITICAL: Key is null or empty string!")
    else:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        try:
            print("Sending 'Hello' to API...")
            response = model.generate_content("Hello")
            print(f"Success! Response: {response.text}")
        except Exception as e:
            print(f"API Call Failed: {e}")

except Exception as e:
    print(f"Debug failed: {e}")
