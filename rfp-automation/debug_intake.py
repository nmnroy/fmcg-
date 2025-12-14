"""Debug the intake agent"""
import os
from dotenv import load_dotenv
load_dotenv()

from agents.intake_agent import RFPIntakeAgent

agent = RFPIntakeAgent()
test_data = {
    "raw_text": "Client: Test Company\nWe need 100 boxes of biscuits and 50 bottles of cooking oil.\nDeadline: 2024-12-31"
}

print("Testing intake agent...")
result = agent.process(test_data)
print("Result:", result)
