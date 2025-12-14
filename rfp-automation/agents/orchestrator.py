"""
LangGraph Orchestrator for RFP Automation

Coordinates the full pipeline:
Intake -> SKU Matching -> Pricing -> Proposal -> Insights

Author: FMCG RFP Automation Team
"""

import os
import logging
from typing import TypedDict, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from langgraph.graph import StateGraph, END

from .intake_agent import RFPIntakeAgent
from .sku_matching_agent import SKUMatchingAgent
from .pricing_agent import PricingAgent
from .proposal_agent import ProposalAgent
from .sales_insight_agent import SalesInsightsAgent
from utils.embeddings import create_embeddings_manager
from utils.pdf_parser import parse_rfp_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RFPState(TypedDict, total=False):
    rfp_id: str
    raw_data: Dict[str, Any]
    intake_result: Dict[str, Any]
    sku_matches: Dict[str, Any]
    pricing: Dict[str, Any]
    proposal: str
    insights: Dict[str, Any]
    status: str
    errors: List[str]


# Lazy initialization of agents
_intake_agent = None
_sku_agent = None
_pricing_agent = None
_proposal_agent = None
_insights_agent = None

_embeddings_manager = None  # lazy init in first node


def _get_intake_agent():
    global _intake_agent
    if _intake_agent is None:
        _intake_agent = RFPIntakeAgent()
    return _intake_agent


def _get_sku_agent():
    global _sku_agent
    if _sku_agent is None:
        _sku_agent = SKUMatchingAgent()
    return _sku_agent


def _get_pricing_agent():
    global _pricing_agent
    if _pricing_agent is None:
        _pricing_agent = PricingAgent()
    return _pricing_agent


def _get_proposal_agent():
    global _proposal_agent
    if _proposal_agent is None:
        _proposal_agent = ProposalAgent()
    return _proposal_agent


def _get_insights_agent():
    global _insights_agent
    if _insights_agent is None:
        _insights_agent = SalesInsightsAgent()
    return _insights_agent


def _get_embeddings_manager() -> Any:
    global _embeddings_manager
    if _embeddings_manager is None:
        logger.info("Initializing SKU embeddings manager...")
        _embeddings_manager = create_embeddings_manager("data/sku_catalog.csv")
    return _embeddings_manager


def intake_node(state: RFPState) -> RFPState:
    logger.info("[Node:intake] Starting intake processing")
    errors = state.get("errors", [])

    try:
        result = _get_intake_agent().process({"raw_text": state["raw_data"]["raw_text"]})
        state["intake_result"] = result
        state["rfp_id"] = result.get("rfp_id", state.get("rfp_id", ""))
        state["status"] = "INTAKE_COMPLETE"
    except Exception as e:
        msg = f"Intake error: {e}"
        logger.error(msg)
        errors.append(msg)
        state["status"] = "INTAKE_FAILED"
    state["errors"] = errors
    return state


def sku_matching_node(state: RFPState) -> RFPState:
    logger.info("[Node:sku_matching] Starting SKU matching")
    errors = state.get("errors", [])

    try:
        intake = state.get("intake_result", {})
        line_items = intake.get("line_items", [])
        rfp_id = state.get("rfp_id", intake.get("rfp_id", ""))

        em = _get_embeddings_manager()
        if em is None:
            raise RuntimeError("Embeddings manager could not be initialized")

        result = _get_sku_agent().process(rfp_id, line_items, em)
        state["sku_matches"] = result
        state["status"] = "SKU_MATCHING_COMPLETE"
    except Exception as e:
        msg = f"SKU matching error: {e}"
        logger.error(msg)
        errors.append(msg)
        state["status"] = "SKU_MATCHING_FAILED"
    state["errors"] = errors
    return state


def pricing_node(state: RFPState) -> RFPState:
    logger.info("[Node:pricing] Starting pricing")
    errors = state.get("errors", [])

    try:
        rfp_id = state.get("rfp_id", "")
        sku_matches = state.get("sku_matches", {})

        # Load pricing rules from file
        import json
        from pathlib import Path

        rules_path = Path("data/pricing_rules.json")
        with rules_path.open("r", encoding="utf-8") as f:
            pricing_rules = json.load(f)

        em = _get_embeddings_manager()

        result = _get_pricing_agent().process(
            rfp_id=rfp_id,
            sku_matches=sku_matches.get("sku_matches", []),
            pricing_rules=pricing_rules,
            client_type="regular",
            embeddings_manager=em,
        )
        state["pricing"] = result
        state["status"] = "PRICING_COMPLETE"
    except Exception as e:
        msg = f"Pricing error: {e}"
        logger.error(msg)
        errors.append(msg)
        state["status"] = "PRICING_FAILED"
    state["errors"] = errors
    return state


def proposal_node(state: RFPState) -> RFPState:
    logger.info("[Node:proposal] Generating proposal document")
    errors = state.get("errors", [])

    try:
        intake = state.get("intake_result", {})
        sku_matches = state.get("sku_matches", {})
        pricing = state.get("pricing", {})

        proposal_md = _get_proposal_agent().process(intake, sku_matches, pricing)
        state["proposal"] = proposal_md
        state["status"] = "PROPOSAL_COMPLETE"
    except Exception as e:
        msg = f"Proposal error: {e}"
        logger.error(msg)
        errors.append(msg)
        state["status"] = "PROPOSAL_FAILED"
    state["errors"] = errors
    return state


def insights_node(state: RFPState) -> RFPState:
    logger.info("[Node:insights] Generating sales insights")
    errors = state.get("errors", [])

    try:
        rfp_id = state.get("rfp_id", "")
        intake = state.get("intake_result", {})
        sku_matches = state.get("sku_matches", {})
        pricing = state.get("pricing", {})

        insights = _get_insights_agent().process(rfp_id, intake, sku_matches, pricing)
        state["insights"] = insights
        state["status"] = "INSIGHTS_COMPLETE"
    except Exception as e:
        msg = f"Insights error: {e}"
        logger.error(msg)
        errors.append(msg)
        state["status"] = "INSIGHTS_FAILED"
    state["errors"] = errors
    return state


def create_rfp_workflow():
    """Create and compile the LangGraph workflow."""
    workflow = StateGraph(RFPState)

    workflow.add_node("intake", intake_node)
    workflow.add_node("sku_matching", sku_matching_node)
    workflow.add_node("pricing", pricing_node)
    workflow.add_node("proposal", proposal_node)
    workflow.add_node("insights", insights_node)

    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "sku_matching")
    workflow.add_edge("sku_matching", "pricing")
    workflow.add_edge("pricing", "proposal")
    workflow.add_edge("proposal", "insights")
    workflow.add_edge("insights", END)

    return workflow.compile()
