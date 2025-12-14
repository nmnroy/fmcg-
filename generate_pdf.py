from reportlab.lib.pagesizes import letter

from reportlab.pdfgen import canvas

from reportlab.lib import colors

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import os

def create_pdf(filename, content):

    doc = SimpleDocTemplate(filename, pagesize=letter)

    styles = getSampleStyleSheet()

    story = []


    # Custom styles

    title_style = styles['Title']

    heading_style = styles['Heading2']
    normal_style = styles['Normal']


    # content is expected to be simple markdown-like text

    lines = content.split('\n')
    

    for line in lines:

        line = line.strip()

        if not line:

            story.append(Spacer(1, 12))
            continue
            

        if line.startswith('**') and line.endswith('**'):

            # Bold heading

            text = line.replace('**', '')

            story.append(Paragraph(text, heading_style))

        elif line.startswith('- '):

            # Bullet point

            text = line[2:]

            story.append(Paragraph(f"• {text}", normal_style))

        elif ':' in line and line.split(':')[0].isupper():

             # Uppercase keys like "CLIENT:"

             story.append(Paragraph(f"<b>{line}</b>", normal_style))

        else:

            story.append(Paragraph(line, normal_style))


    doc.build(story)

    print(f"PDF created: {filename}")


content = """**REQUEST FOR PROPOSAL - FMCG SUPPLY CONTRACT**

**RFP Reference:** SKU-2025-RETAIL-088

**Date:** December 14, 2025

**Client:** Future Retail Group (BigBasket / BlinkIt)


**1. Executive Summary**

We are looking to secure a bulk supply contract for personal care and home hygiene products for our Q1 2026 inventory.


**2. Product Requirements**

Please provide your best distributor pricing for the following:


**A. Hair Care**

- Sunsilk Black Shine Shampoo (180ml) - 500 cases

- Dove Intense Repair Shampoo (650ml) - 200 cases

- Tresemme Keratin Smooth (340ml) - 300 cases


**B. Skin Care**

- Pond's White Beauty Face Wash (100g) - 400 cases

- Vaseline Cocoa Glow Body Lotion (400ml) - 150 cases


**C. Home Hygiene**

- Vim Dishwash Liquid (750ml) - 1000 cases

- Domex Floor Cleaner (1L) - 500 cases


**3. Commercial Terms**

- **Delivery:** Must be delivered to our Bangalore Central Warehouse within 7 days of PO.

- **Payment:** Net 45 days.

- **Shelf Life:** Minimum 80% shelf life remaining upon delivery.


**4. Submission**

Please submit your commercial proposal by Dec 20, 2025 including applicable GST and volume discounts.

"""


output_path = r"c:\\Users\\Lenovo\\OneDrive\\Desktop\\fmcg agentic ai\\sample_fmcg_rfp.pdf"

create_pdf(output_path, content)

