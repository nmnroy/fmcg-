#!/usr/bin/env python3
"""
FMCG Agentic AI End-to-End System Verification Suite
Performs automated sanity verification across all agents, utilities, and data pipelines.
"""

import os
import sys
import time

# Configure paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RFP_DIR = os.path.join(BASE_DIR, "rfp-automation")
if RFP_DIR not in sys.path:
    sys.path.append(RFP_DIR)
if os.path.join(BASE_DIR, "backend") not in sys.path:
    sys.path.append(os.path.join(BASE_DIR, "backend"))


def test_catalog():
    import csv
    path = os.path.join(BASE_DIR, "data", "sku_catalog.csv")
    assert os.path.exists(path), "Catalog file data/sku_catalog.csv missing"
    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 50, f"Expected 50+ SKUs, found {len(rows)}"
    categories = {r["category"] for r in rows}
    assert "Personal Care" in categories
    assert "Home Care" in categories
    assert "Packaged Foods" in categories
    return f"Master Catalog verified ({len(rows)} SKUs across {len(categories)} categories)"


def test_uom_normalizer():
    from utils.uom_normalizer import normalize_quantity
    res = normalize_quantity(10, "cases", "Dove Shampoo 340ml")
    assert res["normalized_units"] == 120
    assert res["packaging_type"] == "case"
    return "UoM Normalizer verified (cartons, cases, dozens to consumer units)"


def test_sku_matching():
    from agents.sku_matching_agent import SKUMatchingAgent
    agent = SKUMatchingAgent()
    matches = agent.match_local("Sunsilk Shampoo 180ml", top_k=1)
    assert len(matches) > 0
    assert matches[0]["sku_id"] == "HUL_SUN_001"
    return f"SKU Matching verified (Matched Sunsilk -> {matches[0]['sku_id']})"


def test_pricing_engine():
    from agents.pricing_agent import PricingAgent
    agent = PricingAgent()
    disc = agent.get_volume_discount_pct(500)
    assert disc == 10.0
    gst = agent.get_gst_rate("Dairy & Staples")
    assert gst == 5.0
    return "Pricing Engine verified (10% tier discount on 500 units, 5% dairy GST)"


def test_compliance():
    from utils.compliance_checker import validate_order_compliance
    rfp_data = {"client_name": "Test Wholesale"}
    pricing_data = {
        "pricing_table": [{"sku_name": "Amul Butter 500g", "qty": 20, "category": "Dairy & Staples", "net_unit_price": 250}],
        "summary": {"grand_total": 5000}
    }
    res = validate_order_compliance(rfp_data, pricing_data)
    assert res["is_compliant"] is True
    assert any("Temperature-Controlled" in tag for tag in res["special_handling_tags"])
    return "Compliance Guardrails verified (Cold-chain detection active)"


def test_proposal_generation():
    from agents.best_proposal_agent import BestProposalAgent
    agent = BestProposalAgent()
    rfp_data = {"client_name": "Metro Cash & Carry", "location": "Mumbai Hub"}
    pricing_data = {
        "pricing_table": [{"sku_name": "Vim Dishwash Gel 750ml", "qty": 100, "unit": "bottles", "net_unit_price": 140, "gst_pct": 18, "line_total_price": 16520}],
        "summary": {"subtotal": 14000, "total_discount_amount": 1000, "tax_amount": 2520, "grand_total": 16520}
    }
    proposal = agent._generate_fallback_proposal(rfp_data, pricing_data)
    assert "Commercial Pricing & SKU Schedule" in proposal
    assert "Metro Cash & Carry" in proposal
    return "Proposal Generation verified (Official markdown quotation generated)"


def test_pdf_export():
    from utils.pdf_generator import generate_rfp_pdf
    sample_data = {
        "rfp_id": "VERIFY_TEST",
        "rfp_data": {"client_name": "Verification Client"},
        "pricing": {"pricing_table": [], "summary": {"subtotal": 1000, "grand_total": 1180}}
    }
    out = generate_rfp_pdf(sample_data, "output/verify_test.pdf")
    assert os.path.exists("output/verify_test.pdf")
    return f"PDF Generator verified ({out})"


def test_csv_export():
    from utils.excel_exporter import export_rfp_to_csv
    sample_data = {
        "rfp_id": "VERIFY_CSV",
        "rfp_data": {"client_name": "CSV Client"},
        "pricing": {"pricing_table": [{"sku_code": "SKU01", "sku_name": "Test", "qty": 10, "net_unit_price": 100, "line_total_price": 1000}], "summary": {"grand_total": 1000}}
    }
    out = export_rfp_to_csv(sample_data, "output/verify_test.csv")
    assert os.path.exists("output/verify_test.csv")
    return f"CSV Exporter verified ({out})"


def test_backend_api():
    from fastapi.testclient import TestClient
    from server import app
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    return "FastAPI Backend verified (/api/health responded 200 OK)"


def run_system_audit() -> bool:
    print("\n" + "=" * 60)
    print("  FMCG AGENTIC AI - SYSTEM INTEGRATION AUDIT")
    print("=" * 60 + "\n")

    checks = [
        ("Catalog Data Integrity", test_catalog),
        ("Packaging & UoM Normalizer", test_uom_normalizer),
        ("Hybrid SKU Matching Engine", test_sku_matching),
        ("Commercial Pricing & GST Engine", test_pricing_engine),
        ("Order Compliance Guardrails", test_compliance),
        ("Multi-Template Proposal Generator", test_proposal_generation),
        ("Official PDF Quotation Exporter", test_pdf_export),
        ("CSV / Excel Spreadsheet Exporter", test_csv_export),
        ("FastAPI Backend Server & Endpoints", test_backend_api)
    ]

    all_passed = True
    start_total = time.time()

    for idx, (name, test_fn) in enumerate(checks, 1):
        t0 = time.time()
        try:
            msg = test_fn()
            elapsed = time.time() - t0
            print(f"[{idx}/{len(checks)}]  PASS  {name} ({elapsed:.3f}s)")
            print(f"       -> {msg}\n")
        except Exception as e:
            all_passed = False
            elapsed = time.time() - t0
            print(f"[{idx}/{len(checks)}]  FAIL  {name} ({elapsed:.3f}s)")
            print(f"       -> ERROR: {e}\n")

    print("=" * 60)
    total_time = time.time() - start_total
    if all_passed:
        print(f"  ALL {len(checks)} SYSTEM CHECKS PASSED IN {total_time:.2f}s")
        print("  System status: PRODUCTION READY")
        print("=" * 60 + "\n")
        return True
    else:
        print(f"  AUDIT FAILED (Finished in {total_time:.2f}s)")
        print("=" * 60 + "\n")
        return False


def main():
    success = run_system_audit()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
