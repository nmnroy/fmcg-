import sys
import os
import json

# Add rfp-automation directory to Python path
sys.path.append(os.path.join(os.getcwd(), 'rfp-automation'))

from agents.sku_matching_agent import SKUMatchingAgent

# Mock intake data
sample_rfp_data = {
    "line_items": [
        {
            "id": "1",
            "description": "Need 50 cases of Sunsilk Black Shine Shampoo 180ml",
            "item_name": "Sunsilk Black Shine Shampoo",
            "specifications": "180ml",
            "quantity": 50
        }
    ]
}

print("Initializing SKU Matching Agent...")
agent = SKUMatchingAgent()
print("Processing sample data...")
result = agent.process(sample_rfp_data)

print("\n--- RAW RESULT ---")
print(json.dumps(result, indent=2))

matches = result.get('matches', [])
if matches:
    print("\n--- TEST CHECK ---")
    first_match = matches[0]
    details = first_match.get('matched_sku_details')
    print(f"Details Field Present: {'YES' if details else 'NO'}")
    print(f"Details Content: {details}")
else:
    print("No matches found.")
