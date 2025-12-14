import sys
import os
import json

# Add rfp-automation directory to Python path
sys.path.append(os.path.join(os.getcwd(), 'rfp-automation'))

from agents.intake_agent import IntakeAgent

sample_text = """
Please quote for the following:
1. Mixer Grinder – 500W – Qty 50
2. Electric Kettle – 1.5L – Qty 100
3. Juicer – 400W – Qty 30
"""

print("Initializing Intake Agent...")
agent = IntakeAgent()
print("Processing sample text...")
result = agent.process(sample_text)

print("\n--- RAW RESULT ---")
print(json.dumps(result, indent=2))

print("\n--- FORMATTED OUTPUT ---")
items = result.get('line_items', [])
for i, item in enumerate(items, 1):
    name = item.get('item_name') or item.get('description', 'Unknown Item')
    spec = item.get('specifications', '')
    qty = item.get('quantity', 'N/A')
    
    line_str = f"{i}. {name}"
    if spec:
        line_str += f" – {spec}"
    line_str += f" – Qty {qty}"
    print(line_str)
