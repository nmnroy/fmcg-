import requests
import time

BASE_URL = "http://localhost:8000"

def wait_for_server():
    for _ in range(10):
        try:
            resp = requests.get(f"{BASE_URL}/")
            if resp.status_code == 200:
                print("✅ Server is up!")
                return True
        except:
            time.sleep(1)
            print("Waiting for server...")
    return False

if wait_for_server():
    # Test Chat
    print("Testing Chat Endpoint...")
    payload = {"message": "Hello", "context": "User is asking for a greeting."}
    try:
        resp = requests.post(f"{BASE_URL}/api/chat", json=payload)
        print(f"Chat Response: {resp.json()}")
    except Exception as e:
        print(f"❌ Chat failed: {e}")
else:
    print("❌ Server failed to start.")
