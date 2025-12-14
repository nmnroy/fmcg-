from utils.gemini_wrapper import GeminiLLM

print("🧪 Testing Multiple API Keys...\n")

# Initialize with multiple keys
llm = GeminiLLM(model_name="gemini-2.5-flash", use_multiple_keys=True)

# Test 5 requests
for i in range(5):
    try:
        response = llm.generate(f"Say 'Test {i+1} successful' in one sentence")
        print(f"✅ Request {i+1}: {response[:60]}...")
    except Exception as e:
        print(f"❌ Request {i+1} failed: {e}")

# Show statistics
print("\n📊 API Key Usage Statistics:")
stats = llm.get_stats()

for key, data in stats.items():
    key_preview = f"...{key[-15:]}"
    print(f"  {key_preview}: {data['calls']} calls, {data['errors']} errors")

print("\n✅ Test complete!")
