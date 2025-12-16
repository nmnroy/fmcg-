"""
RFP Intake & Classification Agent

Parses incoming RFP documents (text/PDF) to extract structured data
and classify relevance for Asian Paints.

Author: FMCG RFP Automation Team
"""

import json
import logging
import os
from typing import Dict, Any, Union

from prompts.agent_prompts import RFP_INTAKE_PROMPT
from utils.gemini_wrapper import GeminiLLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntakeAgent:
    """RFP Intake & Classification Agent"""

    def __init__(self, model_name: str = None, temperature: float = 0.1):
        self.model_name = model_name or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
        self.temperature = temperature
        self.llm = GeminiLLM(model_name=self.model_name)
        logger.info(f"Intake Agent initialized with model: {self.model_name}")

    async def process_async(self, rfp_content: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Process FMCG Order/RFP content (Async)."""
        from utils.json_parser import parse_json_output
        import asyncio
        
        try:
            text_to_process = rfp_content.get("raw_text", str(rfp_content)) if isinstance(rfp_content, dict) else str(rfp_content)
            logger.info(f"Processing intake text: {len(text_to_process)} chars")

            prompt = f"""Process this FMCG Order Text/RFP:
            
            INPUT:
            {text_to_process}
            
            Extract the data according to the System Prompt.
            """

            response = await self.llm.generate_content_async(prompt, system_instruction=RFP_INTAKE_PROMPT)
            return parse_json_output(response)

        except Exception as e:
            logger.error(f"Intake processing failed: {e}", exc_info=True)
            return {"line_items": [], "error": str(e)}

    def process(self, rfp_content: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Sync wrapper"""
        import asyncio
        return asyncio.run(self.process_async(rfp_content))

    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "agent_name": "RFP Intake & Classification Agent",
            "version": "1.0.0",
            "model": self.model_name
        }
