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

content = """**REQUEST FOR PROPOSAL - CLOUD MIGRATION & MANAGED SERVICES**
**RFP Reference:** TECH-2025-CLOUD-088
**Date:** December 11, 2025
**Client:** Global FinTech Solutions Ltd.

**1. Executive Summary**
Global FinTech Solutions aims to migrate its legacy on-premise data center infrastructure to a hybrid cloud environment (AWS/Azure) to improve scalability, security, and operational efficiency.

**2. Scope of Work**

**A. Infrastructure Migration**
- Current State: 500+ Virtual Machines (VMware), 50 TB Oracle Database, 100 TB File Storage.
- Target State: Re-host (Lift & Shift) 40% of workloads, Re-platform 30%, Re-architect 30%.
- Timeline: 12-month phased migration.

**B. Managed Services (3-Year Contract)**
- 24x7 Monitoring & Incident Management (L1/L2/L3 Support).
- Security Operations Center (SOC) integration.
- DevOps Pipeline Management (CI/CD).
- Quarterly Disaster Recovery (DR) drills.

**C. Compliance & Security**
- Must adhere to MAS and RBI data localization norms.
- PCI-DSS Level 1 certification required.

**3. Submission Requirements**
- Technical Architecture Blueprint.
- Migration Strategy.
- Team Structure.
- Commercial Bid.

**4. Evaluation Criteria**
- Technical Competence (40%)
- Commercial competitiveness (30%)
- Security & Compliance approach (30%)
"""

output_path = r"c:\Users\Lenovo\OneDrive\Desktop\fmcg agentic ai\sample_rfp.pdf"
create_pdf(output_path, content)
