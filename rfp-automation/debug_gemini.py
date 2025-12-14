"""Debug Gemini response"""
import os
from dotenv import load_dotenv
load_dotenv()

from utils.gemini_wrapper import GeminiLLM
from utils.json_parser import parse_json_output

llm = GeminiLLM()
prompt = """You are an RFP intake specialist. Extract key information from this RFP and return JSON:

{
  "rfp_id": "Generated automatically",
  "metadata": {
    "client_name": "Extract client name",
    "submission_deadline": "Extract deadline",
    "estimated_value": "Extract value if mentioned",
    "contact_info": "Extract contact details"
  },
  "requirements": {
    "summary": "Brief summary of requirements",
    "technical_specs": ["List key technical requirements"],
    "compliance_requirements": ["List compliance needs"]
  },
  "line_items": [
    {
      "item_description": "Description of item/service",
      "quantity": "Number if specified",
      "unit": "Unit of measure",
      "specifications": "Technical specs"
    }
  ],
  "classification": {
    "industry": "Industry type",
    "priority_score": "1-100 score",
    "complexity": "Low/Medium/High"
  }
}

RFP Data:
{"raw_text": "Client: Test Company\\nWe need 100 boxes of biscuits and 50 bottles of cooking oil.\\nDeadline: 2024-12-31"}

Return ONLY valid JSON."""

print("Testing Gemini...")
response = llm.invoke(prompt)
print("Raw response:", repr(response.content))
print("\nParsed response:")
parsed = parse_json_output(response.content)
print(parsed)
