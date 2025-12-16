import os
import json
import logging
from typing import Dict, Any
from datetime import datetime
from utils.gemini_wrapper import GeminiLLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BestProposalAgent:
    """Best Working Proposal Generation Agent - Robust and Reliable"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
        self.llm = GeminiLLM(model_name=self.model_name)
        logger.info(f"Best Proposal Agent initialized with model: {self.model_name}")
    
    async def process_async(self, rfp_data: Dict[str, Any], pricing_data: Dict[str, Any], insights_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a professional FMCG proposal in markdown format (Async)"""
        from prompts.agent_prompts import PROPOSAL_PROMPT
        import asyncio
        
        try:
            client_name = rfp_data.get('client_name', 'Valued Client')
            total_value = pricing_data.get('summary', {}).get('grand_total', 0)
            
            # Context for prompt
            prompt = f"""Generate a professional FMCG Sales Proposal/Quote.
            
            CLIENT: {client_name}
            TOTAL VALUE: ₹{total_value:,.2f}
            
            Use the PROPOSAL_PROMPT structure.
            """

            response = await self.llm.generate_content_async(prompt, system_instruction=PROPOSAL_PROMPT)
            
            # Clean response text
            proposal_text = response.strip()
            # If wrapped in JSON by mistake, try extracting content
            if proposal_text.startswith('{') and 'content' in proposal_text:
                 try:
                     proposal_text = json.loads(proposal_text).get('content', proposal_text)
                 except: pass

            logger.info(f"Generated proposal for {client_name}")
            return {"content": proposal_text}
            
        except Exception as e:
            logger.error(f"Error generating proposal: {str(e)}")
            return {"content": self._generate_fallback_proposal(rfp_data, pricing_data)}

    def process(self, rfp_data: Dict[str, Any], pricing_data: Dict[str, Any], insights_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync wrapper"""
        import asyncio
        return asyncio.run(self.process_async(rfp_data, pricing_data, insights_data))
    
    def _generate_fallback_proposal(self, rfp_data: Dict[str, Any], pricing_data: Dict[str, Any]) -> str:
        """Generate a fallback proposal for FMCG"""
        client_name = rfp_data.get('client_name', 'Partner')
        total_value = pricing_data.get('summary', {}).get('grand_total', 0)
        
        return f"""# Sales Quote
        
**Client:** {client_name}
**Date:** {datetime.now().strftime('%Y-%m-%d')}

## Commercial Summary
**Total Order Value:** ₹{total_value:,.2f}

Thank you for your business. Please confirm this order for processing.
"""
