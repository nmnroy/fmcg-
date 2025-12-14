"""
Proposal Drafting Agent

Generates a complete client-ready proposal markdown document using
RFP metadata, SKU mapping, and pricing table.

Author: FMCG RFP Automation Team
"""

import logging
import os
from typing import Dict, Any
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate

from prompts.agent_prompts import PROPOSAL_PROMPT
from utils.gemini_wrapper import GeminiLLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProposalAgent:
    """Proposal Drafting Agent"""

    def __init__(self, model_name: str = None, temperature: float = 0):
        self.model_name = model_name or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
        self.temperature = temperature
        self.llm = GeminiLLM(model_name=self.model_name)
        self.prompt = ChatPromptTemplate.from_template(PROPOSAL_PROMPT)
        logger.info(f"Proposal Agent initialized with model: {self.model_name}")

    def process(self, rfp_metadata: Dict[str, Any], sku_mapping: Dict[str, Any], pricing: Dict[str, Any]) -> str:
        """Generate proposal markdown.

        Returns clean markdown string.
        """
        try:
            logger.info(f"Starting proposal generation with metadata: {rfp_metadata.get('metadata', {})}")
            
            client_name = rfp_metadata.get("metadata", {}).get("client_name") or rfp_metadata.get("client_name", "Valued Client")
            logger.info(f"Client name: {client_name}")

            # Validate inputs
            if not rfp_metadata:
                logger.warning("Empty rfp_metadata received")
                rfp_metadata = {"metadata": {"client_name": client_name}}
            
            if not sku_mapping:
                logger.warning("Empty sku_mapping received")
                sku_mapping = {}
                
            if not pricing:
                logger.warning("Empty pricing received")
                pricing = {"summary": {"total_value": 0}}

            # Simple string formatting to avoid JSON brace conflicts
            formatted_prompt = PROPOSAL_PROMPT.replace("{client_name}", client_name)
            formatted_prompt = formatted_prompt.replace("{rfp_metadata}", str(rfp_metadata))
            formatted_prompt = formatted_prompt.replace("{sku_mapping}", str(sku_mapping))
            formatted_prompt = formatted_prompt.replace("{pricing_table}", str(pricing))

            logger.info("Generating proposal markdown via LLM...")
            content = self.llm.generate(formatted_prompt, temperature=self.temperature).strip()
            logger.info(f"LLM response received: {content[:100]}...")

            # Ensure we return plain markdown (strip code fences if any)
            if content.startswith("```"):
                parts = content.split("```", 2)
                if len(parts) >= 3:
                    content = parts[1]
                    # If fenced with language, drop first line
                    lines = content.splitlines()
                    if lines and lines[0].strip().isalpha():
                        content = "\n".join(lines[1:]).strip()

            logger.info("Proposal markdown generated successfully")
            return content
        except Exception as e:
            logger.error(f"Error generating proposal: {e}", exc_info=True)
            # Fallback minimal proposal
            fallback_proposal = (
                f"# Proposal for {client_name if 'client_name' in locals() else 'Valued Client'}\n\n"
                "## Executive Summary\n"
                "We are pleased to submit this proposal for your painting project requirements.\n\n"
                "## Project Scope\n"
                "Based on your RFP, we understand the need for comprehensive painting services.\n\n"
                "## Pricing\n"
                f"Total Project Value: ₹{pricing.get('summary', {}).get('total_value', 0):,.2f}\n\n"
                "## Next Steps\n"
                "We look forward to discussing this proposal further and addressing any questions you may have.\n\n"
                "---\n\n"
                "*Note: This proposal was generated with limited information. Please contact us for a detailed proposal.*"
            )
            return fallback_proposal

    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "agent_name": "Proposal Drafting Agent",
            "version": "1.0.0",
            "model": self.model_name,
            "temperature": self.temperature,
        }
