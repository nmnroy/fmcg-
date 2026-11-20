"""
FMCG RFP Automation CLI Tool
Command line interface for processing RFPs, SKU matching, pricing simulation, and quotation export.
"""

import argparse
import json
import os
import sys

# Ensure repository root and rfp-automation are in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "rfp-automation")))

from agents.orchestrator import run_sequential_pipeline
from utils.excel_exporter import export_rfp_to_csv, export_rfp_to_excel
from utils.pdf_generator import generate_rfp_pdf


def cmd_process(args):
    """Process an RFP order file."""
    if not os.path.exists(args.file):
        print(f"Error: Order file '{args.file}' not found.")
        return 1

    with open(args.file, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"[*] Processing RFP from '{args.file}' (mock_mode={args.mock})...")
    result = run_sequential_pipeline(content, use_mock=args.mock)

    pricing = result.get("pricing", {})
    summary_data = pricing.get("summary", {})
    intake_data = result.get("rfp_data", {})

    summary = {
        "status": result.get("status"),
        "customer": intake_data.get("client_name", "Retail Client"),
        "total_cost": summary_data.get("final_price", 0.0),
        "line_items_count": len(pricing.get("pricing_table", [])),
        "execution_time_seconds": result.get("timing", {}).get("total_pipeline_seconds", 0)
    }
    print("[+] RFP Processing Complete:")
    print(json.dumps(summary, indent=2))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as out_f:
            json.dump(result, out_f, indent=2)
        print(f"[+] Full JSON results saved to: {args.output}")

    if args.pdf:
        pdf_path = generate_rfp_pdf(result, args.pdf)
        print(f"[+] Branded Quotation PDF generated: {pdf_path}")

    if args.csv:
        csv_path = export_rfp_to_csv(result, args.csv)
        print(f"[+] Quotation CSV generated: {csv_path}")

    return 0


def cmd_catalog(args):
    """Search or list items in the SKU catalog."""
    import pandas as pd
    catalog_path = os.path.join(os.path.dirname(__file__), "data", "sku_catalog.csv")
    if not os.path.exists(catalog_path):
        catalog_path = os.path.join(os.path.dirname(__file__), "rfp-automation", "data", "sku_catalog.csv")

    df = pd.read_csv(catalog_path)
    name_col = "name" if "name" in df.columns else "sku_name"
    cost_col = "base_cost" if "base_cost" in df.columns else "base_price"
    unit_col = "unit" if "unit" in df.columns else "uom"

    if args.query:
        q = args.query.lower()
        mask = df[name_col].astype(str).str.lower().str.contains(q) | df["category"].astype(str).str.lower().str.contains(q)
        df = df[mask]

    if args.category:
        df = df[df["category"].astype(str).str.lower() == args.category.lower()]

    limit = args.limit or 20
    print(f"[+] Showing top {min(len(df), limit)} of {len(df)} matching SKUs:")
    cols_to_show = [c for c in ["sku_id", name_col, "category", cost_col, unit_col] if c in df.columns]
    print(df[cols_to_show].head(limit).to_string(index=False))
    return 0


def cmd_verify(args):
    """Run system verification audit."""
    from verify_system import run_system_audit
    success = run_system_audit()
    return 0 if success else 1


def main():
    parser = argparse.ArgumentParser(description="FMCG Intelligent RFP Automation CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # process subcommand
    p_proc = subparsers.add_parser("process", help="Process an RFP order file")
    p_proc.add_argument("file", help="Path to raw order file (.txt or .json)")
    p_proc.add_argument("--mock", action="store_true", default=True, help="Run with deterministic offline mock agents (default: True)")
    p_proc.add_argument("--live", dest="mock", action="store_false", help="Run with live LLM / embedding agents")
    p_proc.add_argument("-o", "--output", help="Save full pipeline JSON to file")
    p_proc.add_argument("--pdf", help="Export branded PDF to specified path")
    p_proc.add_argument("--csv", help="Export CSV quotation to specified path")

    # catalog subcommand
    p_cat = subparsers.add_parser("catalog", help="Search the master FMCG SKU catalog")
    p_cat.add_argument("-q", "--query", help="Keyword search on SKU name or category")
    p_cat.add_argument("-c", "--category", help="Filter by specific FMCG category")
    p_cat.add_argument("-n", "--limit", type=int, default=15, help="Number of results to display")

    # verify subcommand
    subparsers.add_parser("verify", help="Run full system architecture and integration audit")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    if args.command == "process":
        return cmd_process(args)
    elif args.command == "catalog":
        return cmd_catalog(args)
    elif args.command == "verify":
        return cmd_verify(args)


if __name__ == "__main__":
    sys.exit(main())
