"""
Professional FMCG B2B PDF Quotation & Proposal Generator
Uses ReportLab to produce enterprise-grade PDF invoices and quotations.
"""

import os
import io
from datetime import datetime
from typing import Dict, Any, Union

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_rfp_pdf(rfp_result: Dict[str, Any], output_path_or_buffer: Union[str, io.BytesIO] = None) -> Union[str, io.BytesIO]:
    """
    Generates a high-quality B2B quotation PDF from processed RFP result data.
    
    Args:
        rfp_result: The processed result dictionary containing rfp_id, rfp_data, pricing, insights
        output_path_or_buffer: Optional filepath string or io.BytesIO buffer. If None, saves to output/<rfp_id>.pdf
    """
    if output_path_or_buffer is None:
        rfp_id = rfp_result.get("rfp_id", f"RFP_{int(datetime.now().timestamp())}")
        os.makedirs("output", exist_ok=True)
        target = f"output/{rfp_id}_quotation.pdf"
    else:
        target = output_path_or_buffer

    if not REPORTLAB_AVAILABLE:
        # Fallback if ReportLab is not installed in the current environment
        client_name = rfp_result.get("rfp_data", {}).get("client_name") or "Valued Retail Partner"
        pricing_info = rfp_result.get("pricing", {})
        subtotal = pricing_info.get("summary", {}).get("subtotal", 0.0)
        grand_total = pricing_info.get("summary", {}).get("grand_total", 0.0)
        
        fallback_content = f"""%PDF-1.4 (Fallback text representation)
COMMERCIAL QUOTATION
Client: {client_name}
Subtotal: INR {subtotal:,.2f}
Total Payable: INR {grand_total:,.2f}
Note: Install 'reportlab' for high-resolution vector PDF formatting.
"""
        if isinstance(target, io.BytesIO):
            target.write(fallback_content.encode("utf-8"))
            target.seek(0)
            return target
        elif isinstance(target, str):
            with open(target, "w", encoding="utf-8") as f:
                f.write(fallback_content)
            return target

    doc = SimpleDocTemplate(
        target,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    brand_color = colors.HexColor("#1A365D")  # Deep Navy
    accent_color = colors.HexColor("#E53E3E") # Crimson Accent
    text_dark = colors.HexColor("#2D3748")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=brand_color
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#718096")
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=brand_color,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=text_dark
    )

    story = []

    # --- 1. Company Header ---
    client_name = rfp_result.get("rfp_data", {}).get("client_name") or "Valued Retail Partner"
    rfp_id = rfp_result.get("rfp_id", f"RFP-{datetime.now().strftime('%Y%m%d')}")
    date_str = datetime.now().strftime("%B %d, %Y")

    header_data = [
        [
            Paragraph("<b>FMCG AGENTIC AI DISTRIBUTORS</b><br/>Enterprise Wholesale & Institutional Division<br/>GSTIN: 27AABCF1234F1Z9", body_style),
            Paragraph(f"<b>COMMERCIAL QUOTATION</b><br/><b>Ref:</b> {rfp_id}<br/><b>Date:</b> {date_str}", ParagraphStyle('RightHeader', parent=body_style, alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[3.5 * inch, 3.5 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=brand_color, spaceBefore=4, spaceAfter=8))

    # --- 2. Bill To & Deal Context ---
    bill_data = [
        [
            Paragraph(f"<b>BILL TO / CLIENT:</b><br/><b>{client_name}</b><br/>Destination: Pan-India Delivery<br/>Account Tier: Wholesale Modern Trade", body_style),
            Paragraph(f"<b>COMMERCIAL TERMS:</b><br/>Validity: 30 Calendar Days<br/>Payment: Net 30 Days<br/>Dispatch: 48-72 Business Hours", body_style)
        ]
    ]
    bill_table = Table(bill_data, colWidths=[3.5 * inch, 3.5 * inch])
    bill_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(bill_table)
    story.append(Spacer(1, 10))

    # --- 3. Itemized Schedule Table ---
    story.append(Paragraph("SCHEDULE OF ITEMS & PRICING", section_heading))
    
    table_rows = [
        [
            Paragraph("<b>#</b>", table_header_style),
            Paragraph("<b>SKU Description</b>", table_header_style),
            Paragraph("<b>Category</b>", table_header_style),
            Paragraph("<b>Qty</b>", table_header_style),
            Paragraph("<b>Rate (₹)</b>", table_header_style),
            Paragraph("<b>Disc %</b>", table_header_style),
            Paragraph("<b>GST %</b>", table_header_style),
            Paragraph("<b>Total (₹)</b>", table_header_style)
        ]
    ]

    pricing_info = rfp_result.get("pricing", {})
    p_table = pricing_info.get("pricing_table", [])
    
    if not p_table:
        # Generate at least one item from line_items or mock
        p_table = [{
            "sku_name": "FMCG Bulk Assortment",
            "category": "General FMCG",
            "qty": 100,
            "unit": "units",
            "net_unit_price": 150.0,
            "discount_pct": 5.0,
            "gst_pct": 18.0,
            "line_total_price": 17700.0
        }]

    for idx, item in enumerate(p_table, 1):
        name = item.get("sku_name", "Item")[:32]
        cat = item.get("category", "General")[:14]
        qty = f"{item.get('qty', 1)} {item.get('unit', '')}"
        rate = f"₹{item.get('net_unit_price', 0):,.2f}"
        disc = f"{item.get('discount_pct', 0):.1f}%"
        gst = f"{item.get('gst_pct', 18):.0f}%"
        tot = f"₹{item.get('line_total_price', 0):,.2f}"

        table_rows.append([
            Paragraph(str(idx), table_cell_style),
            Paragraph(name, table_cell_style),
            Paragraph(cat, table_cell_style),
            Paragraph(qty, table_cell_style),
            Paragraph(rate, table_cell_style),
            Paragraph(disc, table_cell_style),
            Paragraph(gst, table_cell_style),
            Paragraph(f"<b>{tot}</b>", table_cell_style)
        ])

    items_table = Table(
        table_rows,
        colWidths=[0.3 * inch, 2.5 * inch, 1.1 * inch, 0.7 * inch, 0.8 * inch, 0.5 * inch, 0.4 * inch, 0.9 * inch]
    )
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), brand_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10))

    # --- 4. Financial Summary Card ---
    summary = pricing_info.get("summary", {})
    subtotal = summary.get("subtotal", 0.0)
    discount = summary.get("total_discount_amount", 0.0)
    tax = summary.get("tax_amount", 0.0)
    grand_total = summary.get("grand_total", subtotal + tax)

    financial_data = [
        [Paragraph("Taxable Subtotal:", body_style), Paragraph(f"₹{subtotal:,.2f}", body_style)],
        [Paragraph("Volume Discount Savings:", body_style), Paragraph(f"-₹{discount:,.2f}", body_style)],
        [Paragraph("Applicable GST (CGST+SGST):", body_style), Paragraph(f"₹{tax:,.2f}", body_style)],
        [Paragraph("<b>FINAL PAYABLE AMOUNT:</b>", title_style), Paragraph(f"<b>₹{grand_total:,.2f}</b>", title_style)]
    ]
    fin_table = Table(financial_data, colWidths=[2.2 * inch, 1.6 * inch])
    fin_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor("#EDF2F7")),
        ('LINEBELOW', (0, 2), (-1, 2), 1, brand_color),
    ]))

    terms_text = """<b>Terms & Conditions:</b><br/>
1. All stock guaranteed to have >85% remaining shelf life at dispatch.<br/>
2. 100% credit note replacement on any transit breakage reported within 48 hours.<br/>
3. Free shipping applied for orders exceeding ₹50,000 threshold.
"""
    terms_para = Paragraph(terms_text, body_style)

    closing_table = Table([[terms_para, fin_table]], colWidths=[3.2 * inch, 3.8 * inch])
    closing_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(KeepTogether(closing_table))

    # --- 5. Signatures ---
    story.append(Spacer(1, 16))
    sig_data = [
        [
            Paragraph("Authorized Signatory (FMCG Supply Division)", body_style),
            Paragraph("Client Acceptance Signature & Stamp", ParagraphStyle('RightSig', parent=body_style, alignment=2))
        ]
    ]
    sig_table = Table(sig_data, colWidths=[3.5 * inch, 3.5 * inch])
    story.append(sig_table)

    doc.build(story)
    return target
