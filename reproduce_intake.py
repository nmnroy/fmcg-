import sys
import os

# Add rfp-automation directory to Python path
sys.path.append(os.path.join(os.getcwd(), 'rfp-automation'))

from agents.intake_agent import IntakeAgent

sample_text = """
Please quote for the following:
1. Mixer Grinder – 500W – Qty 50
2. Electric Kettle – 1.5L – Qty 100
3. Juicer – 400W – Qty 30
"""

agent = IntakeAgent()
result = agent.process(sample_text)
print(result)
