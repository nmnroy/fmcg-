"""
Webhook Notification Dispatcher
Sends outbound notifications to ERP, Slack, or webhook endpoints upon RFP quotation approval.
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def prepare_webhook_payload(rfp_result: Dict[str, Any], event_type: str = "rfp.completed") -> Dict[str, Any]:
    """Format standardized event payload for outbound webhooks."""
    return {
        "event": event_type,
        "rfp_id": rfp_result.get("rfp_id", "RFP-UNASSIGNED"),
        "customer": rfp_result.get("customer_name", "Unknown Customer"),
        "total_amount_inr": rfp_result.get("total_cost", 0.0),
        "line_items_count": len(rfp_result.get("line_items", [])),
        "status": rfp_result.get("status", "SUCCESS"),
        "timestamp": rfp_result.get("timestamp", ""),
        "metadata": {
            "source": "FMCG Intelligent RFP Automation Suite",
            "version": "2.0.0"
        }
    }


def dispatch_webhook(webhook_url: str, payload: Dict[str, Any], timeout: int = 5) -> Dict[str, Any]:
    """
    Dispatch payload to the configured webhook endpoint.
    Includes mock fallback for offline or air-gapped test environments.
    """
    if not webhook_url:
        return {"status": "skipped", "reason": "No webhook URL configured"}

    try:
        import urllib.request
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "FMCG-RFP-Bot/2.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return {"status": "success", "status_code": response.status}
    except Exception as exc:
        logger.warning("Webhook dispatch failed to %s: %s", webhook_url, exc)
        return {"status": "failed", "error": str(exc)}
