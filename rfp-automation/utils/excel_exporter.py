"""
FMCG Excel & CSV Quotation Exporter
Generates structured spreadsheet exports for ERP, SAP, and procurement analysis.
"""

import os
import io
import csv
from datetime import datetime
from typing import Dict, Any, Union


def export_rfp_to_csv(rfp_result: Dict[str, Any], output_path_or_buffer: Union[str, io.StringIO, io.BytesIO] = None) -> Union[str, io.BytesIO]:
    """
    Exports RFP quotation line items and financial summary to a clean CSV format.
    """
    rfp_id = rfp_result.get("rfp_id", f"RFP_{int(datetime.now().timestamp())}")
    client_name = rfp_result.get("rfp_data", {}).get("client_name", "Valued Client")
    pricing = rfp_result.get("pricing", {})
    p_table = pricing.get("pricing_table", [])
    summary = pricing.get("summary", {})

    output_is_buffer = isinstance(output_path_or_buffer, (io.StringIO, io.BytesIO))
    string_buffer = io.StringIO() if output_is_buffer else None

    if output_path_or_buffer is None:
        os.makedirs("output", exist_ok=True)
        target_path = f"output/{rfp_id}_quotation.csv"
        f_out = open(target_path, "w", newline="", encoding="utf-8")
    elif output_is_buffer:
        f_out = string_buffer
    else:
        target_path = str(output_path_or_buffer)
        os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
        f_out = open(target_path, "w", newline="", encoding="utf-8")

    try:
        writer = csv.writer(f_out)
        
        # Metadata Header
        writer.writerow(["FMCG COMMERCIAL QUOTATION EXPORT"])
        writer.writerow(["Quotation Ref", rfp_id])
        writer.writerow(["Client Name", client_name])
        writer.writerow(["Export Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])

        # Table Header
        writer.writerow([
            "Item #",
            "SKU Code",
            "SKU Name",
            "Category",
            "Quantity",
            "Unit",
            "List Unit Price (INR)",
            "Volume Discount %",
            "Net Unit Price (INR)",
            "GST %",
            "GST Amount (INR)",
            "Line Total (INR)"
        ])

        # Table Rows
        for idx, row in enumerate(p_table, 1):
            writer.writerow([
                idx,
                row.get("sku_code", "GEN-01"),
                row.get("sku_name", "Item"),
                row.get("category", "General"),
                row.get("qty", 1),
                row.get("unit", "units"),
                f"{row.get('unit_price_base', 0):.2f}",
                f"{row.get('discount_pct', 0):.1f}",
                f"{row.get('net_unit_price', 0):.2f}",
                f"{row.get('gst_pct', 18):.1f}",
                f"{row.get('gst_amount', 0):.2f}",
                f"{row.get('line_total_price', 0):.2f}"
            ])

        writer.writerow([])
        writer.writerow(["FINANCIAL SUMMARY"])
        writer.writerow(["Gross MRP Value (INR)", f"{summary.get('gross_mrp_value', 0):.2f}"])
        writer.writerow(["Total Volume Savings (INR)", f"{summary.get('total_discount_amount', 0):.2f}"])
        writer.writerow(["Taxable Subtotal (INR)", f"{summary.get('subtotal', 0):.2f}"])
        writer.writerow(["Total GST (INR)", f"{summary.get('tax_amount', 0):.2f}"])
        writer.writerow(["Grand Total Payable (INR)", f"{summary.get('grand_total', 0):.2f}"])

    finally:
        if not output_is_buffer:
            f_out.close()

    if output_is_buffer:
        bytes_io = io.BytesIO(string_buffer.getvalue().encode("utf-8"))
        bytes_io.seek(0)
        return bytes_io

    return target_path


def export_rfp_to_excel(rfp_result: Dict[str, Any], output_path_or_buffer: Union[str, io.BytesIO] = None) -> Union[str, io.BytesIO]:
    """
    Exports RFP quotation to Excel (.xlsx) if pandas/openpyxl is available, otherwise falls back to CSV.
    """
    try:
        import pandas as pd
        pricing = rfp_result.get("pricing", {})
        p_table = pricing.get("pricing_table", [])
        
        df_items = pd.DataFrame(p_table)
        
        if output_path_or_buffer is None:
            rfp_id = rfp_result.get("rfp_id", f"RFP_{int(datetime.now().timestamp())}")
            os.makedirs("output", exist_ok=True)
            target = f"output/{rfp_id}_quotation.xlsx"
        else:
            target = output_path_or_buffer

        with pd.ExcelWriter(target, engine="openpyxl" if "openpyxl" in sys.modules else None) as writer:
            df_items.to_excel(writer, sheet_name="Line Items", index=False)
            
            summary_data = [{"Metric": k, "Value": v} for k, v in pricing.get("summary", {}).items()]
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)
            
        return target
    except Exception:
        # Fallback to CSV
        return export_rfp_to_csv(rfp_result, output_path_or_buffer)
