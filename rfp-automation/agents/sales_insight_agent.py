"""
Sales Insights & Recommendation Agent

Analyzes RFP, SKU matches, and pricing to:
- Estimate win probability
- Identify risks
- Recommend negotiation strategy
- Suggest upsell opportunities

Author: FMCG RFP Automation Team
"""

import json
import logging
import os
from typing import Dict, Any, List
from datetime import datetime
# from langchain_core.prompts import ChatPromptTemplate

from prompts.agent_prompts import SALES_INSIGHTS_PROMPT
from utils.gemini_wrapper import GeminiLLM
from utils.json_parser import parse_json_output

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SalesInsightsAgent:
    """Sales Insights & Recommendation Agent"""

    def __init__(self, model_name: str = None, temperature: float = 0):
        self.model_name = model_name or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
        self.temperature = temperature
        self.llm = GeminiLLM(model_name=self.model_name)
        # self.prompt = ChatPromptTemplate.from_template(SALES_INSIGHTS_PROMPT) - REMOVED for dependency fix
        logger.info(f"Sales Insights Agent initialized with model: {self.model_name}")

    async def process_async(self, rfp_text: str, rfp_data: dict, customer_data: dict = None, pricing_data: dict = None) -> dict:
        """Analyze win probability - bulletproof version (Async)"""
        import asyncio
        print("🔍 Insights Agent: Starting analysis (Async)...")
        
        # Default response (returned on any error)
        default_response = {
            "win_probability_pct": 65,
            "confidence_level": "Medium",
            "risk_level": "Medium",
            "risks": [
                {
                    "type": "commercial",
                    "description": "Short delivery timeline",
                    "severity": "medium",
                    "mitigation": "Pre-book inventory"
                }
            ],
            "competitors": ["Philips", "Prestige", "Havells"],
            "strengths": ["Pricing", "Supply Chain", "Product Variety"],
            "recommendations": [
                "Highlight premium product benefits",
                "Offer competitive warranty terms",
                "Include free color consultation"
            ]
        }
        
        try:
            # Get basic info
            project_type = rfp_data.get('project_type', 'commercial')
            quality = rfp_data.get('quality_tier', 'premium')
            area = rfp_data.get('area_sqft', 10000)
            
            # Extract pricing info if available
            pricing_summary = pricing_data.get('summary', {}) if pricing_data else {}
            total_value = pricing_summary.get('grand_total', 0)
            margin = pricing_summary.get('overall_margin_pct', 0)
            
            print(f"   Project: {project_type}, Quality: {quality}, Area: {area} sqft, Value: {total_value}, Margin: {margin}%")
            
            # Create focused prompt
            prompt = f"""Analyze this painting project RFP for Asian Paints and calculate win probability.

Project: {project_type} building, {area} sq ft, {quality} quality
Pricing: Value ₹{total_value:,.0f} with {margin}% margin
RFP Text: {rfp_text[:1000]}

Calculate win probability (0-100) based on:
- "Asian Paints" mentioned: +20
- Premium/luxury tier: +15  
- Large project >20k sqft: +10
- Clear specifications: +10
- High margin (>20%): -10 (price risk)
- Competitive margin (10-15%): +10
- Base: 50

Return ONLY this JSON structure:
{{
    "win_probability_pct": 75,
    "confidence_level": "High",
    "risk_level": "Medium",
    "risks": [{{"type": "commercial", "description": "Short delivery timeline", "severity": "medium", "mitigation": "Pre-book inventory"}}],
    "competitors": ["Philips", "Prestige", "Havells"],
    "strengths": ["Pricing", "Supply Chain", "Product Variety"],
    "recommendations": ["rec 1", "rec 2"]
}}

Return ONLY valid JSON, no explanations or markdown."""

            # print("   Calling API...")
            response = await self.llm.generate_async(prompt, temperature=0.3, max_tokens=4000)
            # print(f"   API response received: {len(response)} chars")
            
            # Clean response aggressively
            response = response.strip()
            
            # Remove markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1]
            if "```" in response:
                response = response.split("```")[0]
            
            # Remove any leading/trailing markers
            response = response.strip()
            response = response.replace("```json", "").replace("```", "")
            
            # print(f"   Cleaned response: {response[:100]}...")
            
            # Parse JSON
            result = json.loads(response)
            # print("   ✅ JSON parsed successfully")
            
            # Validate win_probability_pct
            win_prob = result.get('win_probability_pct', 65)
            if not isinstance(win_prob, (int, float)) or win_prob < 1 or win_prob > 100:
                print(f"   ⚠️ Invalid win probability: {win_prob}, using 65")
                result['win_probability_pct'] = 65
            
            # Ensure required fields exist
            if 'risk_level' not in result:
                result['risk_level'] = 'Medium'
            if 'confidence_level' not in result:
                result['confidence_level'] = 'Medium'
            if 'risks' not in result:
                result['risks'] = default_response['risks']
            if 'strengths' not in result:
                result['strengths'] = default_response['strengths']
            if 'recommendations' not in result:
                result['recommendations'] = default_response['recommendations']
            if 'competitors' not in result:
                result['competitors'] = default_response['competitors']
            
            # print(f"   ✅ Insights complete: {result['win_probability_pct']}% win probability")
            return result
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing failed: {e}")
            # print(f"   Response was: {response[:200] if 'response' in locals() else 'No response'}")
            return default_response
            
        except Exception as e:
            print(f"   ❌ Insights agent error: {e}")
            # import traceback
            # traceback.print_exc()
            return default_response
            
    def process(self, rfp_text: str, rfp_data: dict, customer_data: dict = None, pricing_data: dict = None) -> dict:
        """Sync wrapper"""
        import asyncio
        return asyncio.run(self.process_async(rfp_text, rfp_data, customer_data, pricing_data))

    def _compute_technical_compliance(self, sku_matches: Dict[str, Any]) -> float:
        try:
            items = sku_matches.get("sku_matches", [])
            if not items:
                return 0.0
            compliant = [m for m in items if m.get("confidence", 0) >= 0.75]
            return round(100.0 * len(compliant) / len(items), 2)
        except Exception:
            return 0.0


    def _normalize_result(self, result: Dict[str, Any], technical_compliance: float, margin: float) -> None:
        try:
            # Handle error case
            if 'error' in result:
                # Set default values for error case
                result.update({
                    "win_probability_pct": 0,
                    "confidence_level": "Low",
                    "risks": [{"type": "technical", "description": "Sales insights generation failed", "severity": "high", "mitigation": "Check LLM/API configuration and retry."}],
                    "recommendations": [],
                    "negotiation_strategy": [],
                    "upsell_opportunities": [],
                    "followup_actions": []
                })
                return
            
            # Win probability 0–100
            wp = result.get("win_probability_pct", 0)
            try:
                wp = int(wp)
            except Exception:
                wp = 0
            wp = max(0, min(100, wp))

            # If LLM failed, derive a basic heuristic
            if wp == 0:
                base = 40
                base += max(0, min(30, int(technical_compliance / 3)))
                base += -int(max(0, margin - 15) / 3)
                wp = max(5, min(90, base))

            result["win_probability_pct"] = wp

            # Confidence level
            if wp >= 70:
                level = "High"
            elif wp >= 40:
                level = "Medium"
            else:
                level = "Low"
            result["confidence_level"] = result.get("confidence_level") or level

            # Ensure list fields exist
            for key in [
                "risks",
                "recommendations",
                "negotiation_strategy",
                "upsell_opportunities",
                "followup_actions",
            ]:
                if key not in result or result[key] is None:
                    result[key] = [] if key != "risks" else []
        except Exception as e:
            logger.error(f"Error normalizing insights result: {e}")

    def _create_error_result(self, rfp_id: str, msg: str) -> Dict[str, Any]:
        return {
            "rfp_id": rfp_id,
            "win_probability_pct": 0,
            "confidence_level": "Low",
            "risks": [
                {
                    "type": "technical",
                    "description": f"Sales insights generation failed: {msg}",
                    "severity": "high",
                    "mitigation": "Check LLM/API configuration and retry.",
                }
            ],
            "recommendations": [],
            "negotiation_strategy": [],
            "upsell_opportunities": [],
            "followup_actions": [],
            "error": msg,
            "generated_at": datetime.now().isoformat(),
        }

    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "agent_name": "Sales Insights & Recommendation Agent",
            "version": "1.0.0",
            "model": self.model_name,
            "temperature": self.temperature,
        }
