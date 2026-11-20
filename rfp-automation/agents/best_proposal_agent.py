import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from utils.gemini_wrapper import GeminiLLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROPOSAL_TEMPLATES = {
    "standard": "Standard Commercial Quotation",
    "enterprise": "Enterprise B2B Supply Agreement",
    "express": "Express Fast-Track Restocking Quote",
    "wholesale": "Wholesale Volume Discount Contract"
}


class BestProposalAgent:
    """Enterprise FMCG Proposal & Quotation Generator with Multi-Template Support"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
        self.llm = GeminiLLM(model_name=self.model_name)
        logger.info(f"Best Proposal Agent initialized with model: {self.model_name}")
    
    async def process_async(
        self,
        rfp_data: Dict[str, Any],
        pricing_data: Dict[str, Any],
        insights_data: Dict[str, Any],
        template_style: str = "standard"
    ) -> Dict[str, Any]:
        """Generate a professional FMCG proposal in markdown format (Async)"""
        from prompts.agent_prompts import PROPOSAL_PROMPT
        
        try:
            client_name = rfp_data.get('client_name') or 'Valued Retail Partner'
            pricing_summary = pricing_data.get('summary', {}) if pricing_data else {}
            total_value = pricing_summary.get('grand_total', 0.0)
            subtotal = pricing_summary.get('subtotal', 0.0)
            tax_amount = pricing_summary.get('tax_amount', 0.0)
            discount = pricing_summary.get('total_discount_amount', 0.0)
            
            line_items = pricing_data.get('pricing_table', [])
            items_str = "\n".join([
                f"- {item.get('sku_name', 'Item')}: {item.get('qty', 1)} {item.get('unit', 'units')} @ ₹{item.get('net_unit_price', 0):,.2f} = ₹{item.get('line_total_price', 0):,.2f}"
                for item in line_items[:15]
            ])
            
            prompt = f"""Generate a professional FMCG B2B Sales Proposal / Quotation.

TEMPLATE STYLE: {template_style.upper()} ({PROPOSAL_TEMPLATES.get(template_style, 'Standard')})
CLIENT: {client_name}
TOTAL PROPOSAL VALUE: ₹{total_value:,.2f}
TAXABLE SUBTOTAL: ₹{subtotal:,.2f}
VOLUME SAVINGS APPLIED: ₹{discount:,.2f}
GST TAX AMOUNT: ₹{tax_amount:,.2f}

LINE ITEMS:
{items_str}

KEY COMMERCIAL TERMS:
- Payment terms: Net 30 days
- Minimum guaranteed shelf-life: >85% at dispatch
- Transit insurance: Included
- Dispatch SLA: Within 48-72 hours of PO confirmation

Generate structured Markdown with:
1. Executive Header & Reference Number
2. Commercial Executive Summary
3. Itemized Quotation Table (SKU, Qty, Unit Rate, GST %, Total)
4. Commercial Terms & Payment Conditions
5. Quality & Shelf-Life Assurance
6. Acceptance & Authorized Sign-off Block
"""

            response = await self.llm.generate_content_async(prompt, system_instruction=PROPOSAL_PROMPT)
            
            proposal_text = response.strip()
            if proposal_text.startswith('{') and 'content' in proposal_text:
                try:
                    proposal_text = json.loads(proposal_text).get('content', proposal_text)
                except Exception:
                    pass

            logger.info(f"Generated proposal for {client_name} using style {template_style}")
            return {
                "content": proposal_text,
                "template_style": template_style,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating proposal via LLM: {str(e)}. Generating rich deterministic proposal.")
            return {
                "content": self._generate_fallback_proposal(rfp_data, pricing_data, template_style),
                "template_style": template_style,
                "generated_at": datetime.now().isoformat()
            }

    def process(
        self,
        rfp_data: Dict[str, Any],
        pricing_data: Dict[str, Any],
        insights_data: Dict[str, Any],
        template_style: str = "standard"
    ) -> Dict[str, Any]:
        """Sync wrapper"""
        import asyncio
        return asyncio.run(self.process_async(rfp_data, pricing_data, insights_data, template_style))
    
    def _generate_fallback_proposal(
        self,
        rfp_data: Dict[str, Any],
        pricing_data: Dict[str, Any],
        template_style: str = "standard"
    ) -> str:
        """Generate a complete, professional FMCG quotation markdown document"""
        client_name = rfp_data.get('client_name') or 'Valued Retail Partner'
        location = rfp_data.get('location', 'Pan-India Distribution')
        pricing_summary = pricing_data.get('summary', {}) if pricing_data else {}
        total_value = pricing_summary.get('grand_total', 0.0)
        subtotal = pricing_summary.get('subtotal', 0.0)
        tax = pricing_summary.get('tax_amount', 0.0)
        discount = pricing_summary.get('total_discount_amount', 0.0)
        
        table_rows = []
        p_table = pricing_data.get('pricing_table', [])
        for i, item in enumerate(p_table, 1):
            name = item.get('sku_name', 'FMCG Item')
            qty = item.get('qty', 1)
            unit = item.get('unit', 'units')
            unit_price = item.get('net_unit_price', 0.0)
            gst = item.get('gst_pct', 18)
            line_tot = item.get('line_total_price', 0.0)
            table_rows.append(f"| {i} | {name} | {qty} {unit} | ₹{unit_price:,.2f} | {gst}% | ₹{line_tot:,.2f} |")

        table_md = "\n".join(table_rows) if table_rows else "| 1 | Standard FMCG Assortment | 100 units | ₹150.00 | 18% | ₹17,700.00 |"

        ref_id = f"FMCG-QUO-{datetime.now().strftime('%Y%m%d-%H%M')}"
        today_str = datetime.now().strftime('%B %d, %Y')

        return f"""# B2B FMCG Supply Proposal & Commercial Quotation

**Quotation Reference:** `{ref_id}`  
**Date:** {today_str}  
**Client / Account:** {client_name}  
**Delivery Destination:** {location}  
**Proposal Type:** {PROPOSAL_TEMPLATES.get(template_style, 'Standard Commercial Quote')}

---

## 1. Executive Summary
We are pleased to present our official B2B supply quotation for your upcoming procurement requirements. As a premier authorized distributor of fast-moving consumer goods, we guarantee manufacturer-direct pricing, 100% genuine merchandise, and adherence to top-tier service level agreements (SLAs).

---

## 2. Commercial Pricing & SKU Schedule

| # | Item Description | Order Qty | Net Unit Rate | GST Slab | Total (Incl. GST) |
|:---|:---|:---:|:---:|:---:|:---:|
{table_md}

---

## 3. Financial Summary

| Financial Component | Amount (INR) |
|:---|---:|
| **Gross Order Value (List Price):** | **₹{subtotal + discount:,.2f}** |
| Volume Trade Discount Applied: | -₹{discount:,.2f} |
| **Taxable Order Subtotal:** | **₹{subtotal:,.2f}** |
| Goods & Services Tax (CGST + SGST): | +₹{tax:,.2f} |
| **Final Commercial Payable Amount:** | **₹{total_value:,.2f}** |

> *🎉 This proposal includes **₹{discount:,.2f}** in direct volume tier savings.*

---

## 4. Terms of Supply & Service Level Agreement

- **Payment Terms:** Net 30 days from invoice date via RTGS / NEFT.
- **Delivery Timeline:** Dispatch within 48 to 72 business hours post-PO confirmation.
- **Shelf-Life Guarantee:** All delivered consumables and packaged goods are guaranteed to have a minimum **>85% remaining shelf life**.
- **Freight & Insurance:** Comprehensive transit insurance is included; free delivery applied for orders exceeding ₹50,000.
- **Damages & Returns:** 100% immediate credit note issued for transit damages reported within 48 hours of receipt.
- **Validity:** Commercial rates in this quotation are valid for **30 calendar days** from issuance.

---

## 5. Acceptance & Authorization

| Authorized Signatory (Supplier) | Authorized Signatory (Client) |
|:---|:---|
| **Signature:** __________________________ | **Signature:** __________________________ |
| **Name:** FMCG Institutional Sales Head | **Name:** {client_name} Procurement Officer |
| **Date:** {today_str} | **Date:** __________________________ |
"""
