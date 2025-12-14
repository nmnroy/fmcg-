"""Debug parsing issue"""
import os
from dotenv import load_dotenv
load_dotenv()

from agents.intake_agent import RFPIntakeAgent

agent = RFPIntakeAgent()
test_data = {
    "raw_text": "Client: Test Company\nWe need 100 boxes of biscuits and 50 bottles of cooking oil.\nDeadline: 2024-12-31"
}

# Test just the parsing part
formatted_prompt = agent.prompt.format(rfp_data=test_data)
print("Prompt length:", len(formatted_prompt))
print("\nFirst 500 chars of prompt:")
print(formatted_prompt[:500])

response = agent.llm.invoke(formatted_prompt)
print("\nRaw response content:")
print(repr(response.content[:200]))

from utils.json_parser import parse_json_output
parsed = parse_json_output(response.content)
print("\nParsed result keys:", list(parsed.keys()) if isinstance(parsed, dict) else "Not a dict")
print("rfp_id value:", parsed.get('rfp_id', 'NOT FOUND') if isinstance(parsed, dict) else "Not a dict")
