"""
LangGraph & Sequential Pipeline Orchestrator for FMCG RFP Automation

Coordinates the full multi-agent pipeline:
Intake -> SKU Matching -> Pricing -> Compliance Guardrails -> Insights -> Proposal

Author: FMCG RFP Automation Team
"""

import os
import time
import logging
from typing import TypedDict, Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

from utils.compliance_checker import validate_order_compliance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RFPState(TypedDict, total=False):
    rfp_id: str
    raw_data: Dict[str, Any]
    intake_result: Dict[str, Any]
    sku_matches: Dict[str, Any]
    pricing: Dict[str, Any]
    compliance: Dict[str, Any]
    proposal: str
    insights: Dict[str, Any]
    status: str
    errors: List[str]
    timing: Dict[str, float]


def run_sequential_pipeline(raw_text: str, rfp_id: Optional[str] = None, use_mock: bool = False) -> Dict[str, Any]:
    """
    Robust sequential orchestrator that runs all FMCG agents with timing,
    compliance verification, and graceful error boundaries.
    """
    start_time = time.time()
    timing: Dict[str, float] = {}
    errors: List[str] = []
    
    rfp_id = rfp_id or f"ORDER_{int(time.time())}"

    # 1. Select Agents
    if use_mock:
        from agents.mock_agents import (
            MockIntakeAgent, MockSKUMatchingAgent, MockPricingAgent,
            MockSalesInsightsAgent, MockBestProposalAgent
        )
        intake_agent = MockIntakeAgent()
        sku_agent = MockSKUMatchingAgent()
        pricing_agent = MockPricingAgent()
        insights_agent = MockSalesInsightsAgent()
        proposal_agent = MockBestProposalAgent()
    else:
        from agents.intake_agent import IntakeAgent
        from agents.sku_matching_agent import SKUMatchingAgent
        from agents.pricing_agent import PricingAgent
        from agents.sales_insight_agent import SalesInsightsAgent
        from agents.best_proposal_agent import BestProposalAgent

        intake_agent = IntakeAgent()
        sku_agent = SKUMatchingAgent()
        pricing_agent = PricingAgent()
        insights_agent = SalesInsightsAgent()
        proposal_agent = BestProposalAgent()

    # Step 1: Intake
    t0 = time.time()
    try:
        intake_result = intake_agent.process({"raw_text": raw_text})
    except Exception as e:
        logger.error(f"Intake failed: {e}")
        errors.append(f"Intake: {e}")
        intake_result = {"line_items": [], "client_name": "Retail Client"}
    timing["intake_seconds"] = round(time.time() - t0, 2)

    # Step 2: SKU Matching
    t0 = time.time()
    try:
        sku_matches = sku_agent.process(intake_result)
    except Exception as e:
        logger.error(f"SKU matching failed: {e}")
        errors.append(f"SKU Matching: {e}")
        sku_matches = {"matches": []}
    timing["sku_matching_seconds"] = round(time.time() - t0, 2)

    # Step 3: Pricing
    t0 = time.time()
    try:
        pricing_result = pricing_agent.process(intake_result, sku_matches)
    except Exception as e:
        logger.error(f"Pricing failed: {e}")
        errors.append(f"Pricing: {e}")
        pricing_result = {"pricing_table": [], "summary": {}}
    timing["pricing_seconds"] = round(time.time() - t0, 2)

    # Step 4: Compliance Guardrails
    t0 = time.time()
    compliance_result = validate_order_compliance(intake_result, pricing_result)
    timing["compliance_seconds"] = round(time.time() - t0, 2)

    # Step 5: Sales Insights
    t0 = time.time()
    try:
        insights_result = insights_agent.process(
            rfp_text=raw_text,
            rfp_data=intake_result,
            pricing_data=pricing_result
        )
    except Exception as e:
        logger.error(f"Insights failed: {e}")
        errors.append(f"Insights: {e}")
        insights_result = {"win_probability_pct": 65, "risk_level": "Medium"}
    timing["insights_seconds"] = round(time.time() - t0, 2)

    # Step 6: Proposal Generation
    t0 = time.time()
    try:
        proposal_dict = proposal_agent.process(intake_result, pricing_result, insights_result)
        proposal_content = proposal_dict.get("content", "")
    except Exception as e:
        logger.error(f"Proposal failed: {e}")
        errors.append(f"Proposal: {e}")
        proposal_content = "Quotation generated."
    timing["proposal_seconds"] = round(time.time() - t0, 2)

    timing["total_pipeline_seconds"] = round(time.time() - start_time, 2)

    return {
        "rfp_id": rfp_id,
        "rfp_data": intake_result,
        "sku_matches": sku_matches,
        "pricing": pricing_result,
        "compliance": compliance_result,
        "insights": insights_result,
        "proposal": {"content": proposal_content},
        "errors": errors,
        "timing": timing,
        "status": "COMPLETED" if not errors else "COMPLETED_WITH_WARNINGS"
    }
