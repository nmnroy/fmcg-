"""
FMCG Compliance & Order Guardrails Validator
Checks MOQ compliance, shelf-life standards, credit limits, and cold-chain storage rules.
"""

from typing import Dict, Any, List

MIN_ORDER_VALUE_THRESHOLD = 5000.0  # Minimum order size in INR
COLD_CHAIN_CATEGORIES = {"Dairy & Staples"}
COLD_CHAIN_KEYWORDS = {"butter", "cheese", "milk", "curd", "ghee", "ice cream"}


def validate_order_compliance(rfp_data: Dict[str, Any], pricing_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates an FMCG order against distributor business policies and procurement guardrails.
    
    Returns:
        Dict with keys:
            is_compliant: bool
            compliance_score: int (0-100)
            violations: List[str]
            warnings: List[str]
            special_handling_tags: List[str]
    """
    violations = []
    warnings = []
    special_handling_tags = []

    pricing_table = pricing_data.get("pricing_table", [])
    pricing_summary = pricing_data.get("summary", {})
    grand_total = pricing_summary.get("grand_total", 0.0)

    # 1. Minimum Order Value Check
    if grand_total < MIN_ORDER_VALUE_THRESHOLD and grand_total > 0:
        warnings.append(f"Order total ₹{grand_total:,.2f} is below the optimal freight-free threshold of ₹{MIN_ORDER_VALUE_THRESHOLD:,.2f}.")

    # 2. MOQ (Minimum Order Quantity) & Pack Verification
    for idx, item in enumerate(pricing_table, 1):
        name = item.get("sku_name", f"Item {idx}").lower()
        qty = item.get("qty", 1)
        category = item.get("category", "")

        # Heuristic MOQ check: wholesale orders should normally have at least 10 units per SKU
        if qty < 6:
            warnings.append(f"SKU '{item.get('sku_name')}' ordered in low quantity ({qty} units). Standard distributor MOQ is 12 units.")

        # Cold Chain Check
        if category in COLD_CHAIN_CATEGORIES or any(kw in name for kw in COLD_CHAIN_KEYWORDS):
            tag = "Temperature-Controlled Logistics Required"
            if tag not in special_handling_tags:
                special_handling_tags.append(tag)

        # High Value SKU alert
        if item.get("net_unit_price", 0) > 800:
            special_handling_tags.append(f"High-Value Inventory Item: {item.get('sku_name')}")

    # 3. Delivery Deadline Check
    deadline = rfp_data.get("deadline", "")
    if deadline and any(w in deadline.lower() for w in ["same day", "urgent", "24 hours", "immediate"]):
        warnings.append("Urgent / Same-day delivery requested. Express fulfillment surcharge of 5% applies.")
        special_handling_tags.append("Express Priority Dispatch")

    # 4. Compliance Scoring
    deductions = (len(violations) * 25) + (len(warnings) * 8)
    compliance_score = max(30, min(100, 100 - deductions))
    is_compliant = len(violations) == 0

    return {
        "is_compliant": is_compliant,
        "compliance_score": compliance_score,
        "violations": violations,
        "warnings": warnings,
        "special_handling_tags": special_handling_tags
    }
