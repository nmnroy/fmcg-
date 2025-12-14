import sys
import os
import json

# Add project root to path
sys.path.append(os.path.join(os.getcwd(), 'rfp-automation'))

from agents.intake_agent import IntakeAgent

def debug_intake():
    print("Initializing Intake Agent...")
    agent = IntakeAgent()
    
    file_path = "sample_fmcg_order_2.txt"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Reading {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    print("Processing...")
    try:
        result = agent.process(content)
        print("\n--- RESULT ---")
        print(json.dumps(result, indent=2))
        
        items = result.get("line_items", [])
        print(f"\nExtracted {len(items)} items.")
        
        if len(items) == 0:
            print("FAILURE: No items extracted.")
        else:
            print("SUCCESS: Items extracted.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_intake()
