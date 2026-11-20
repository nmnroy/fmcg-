"""
CLI and Utility Bridge for FMCG RFP PDF Generation
"""
import os
import sys

# Ensure rfp-automation is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RFP_DIR = os.path.join(BASE_DIR, "rfp-automation")
if RFP_DIR not in sys.path:
    sys.path.append(RFP_DIR)

from utils.pdf_generator import generate_rfp_pdf

def create_sample_quotation_pdf(output_filename: str = "output/sample_fmcg_quotation.pdf"):
    """Generates a demo FMCG commercial quote PDF"""
    sample_data = {
        "rfp_id": "ORDER_DEMO_2026",
        "rfp_data": {
            "client_name": "Metro Cash & Carry Wholesale",
            "location": "Regional Hub Mumbai"
        },
        "pricing": {
            "pricing_table": [
                {"sku_name": "Surf Excel Matic Top Load 2kg", "category": "Home Care", "qty": 120, "unit": "packs", "net_unit_price": 448.80, "discount_pct": 6.5, "gst_pct": 18, "line_total_price": 63550.08},
                {"sku_name": "Dove Hair Fall Rescue Shampoo 340ml", "category": "Personal Care", "qty": 240, "unit": "bottles", "net_unit_price": 233.75, "discount_pct": 6.5, "gst_pct": 18, "line_total_price": 66201.00},
                {"sku_name": "Vim Dishwash Gel 750ml", "category": "Home Care", "qty": 300, "unit": "bottles", "net_unit_price": 144.92, "discount_pct": 6.5, "gst_pct": 18, "line_total_price": 51301.68},
                {"sku_name": "Nescafe Classic Coffee Jar 100g", "category": "Beverages", "qty": 150, "unit": "jars", "net_unit_price": 310.20, "discount_pct": 6.0, "gst_pct": 12, "line_total_price": 52113.60},
                {"sku_name": "Aashirvaad Pure Cow Ghee 1L", "category": "Dairy & Staples", "qty": 80, "unit": "tins", "net_unit_price": 630.50, "discount_pct": 3.0, "gst_pct": 5, "line_total_price": 52962.00}
            ],
            "summary": {
                "subtotal": 244580.00,
                "total_discount_amount": 16240.00,
                "tax_amount": 41548.36,
                "grand_total": 286128.36,
                "overall_margin_pct": 18.5
            }
        }
    }
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    out = generate_rfp_pdf(sample_data, output_filename)
    print(f"✅ Generated sample FMCG quotation PDF at: {out}")
    return out

if __name__ == "__main__":
    create_sample_quotation_pdf()
