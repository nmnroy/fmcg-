# FMCG Agentic AI Architecture

## Overview
The **FMCG Agentic AI Platform** is an enterprise-grade autonomous response system designed for fast-moving consumer goods (FMCG) distributors, manufacturers, and modern trade procurement teams. It automates the end-to-end lifecycle of converting unstructured RFPs, purchase orders, and store replenishment requests into verified, priced, and compliant commercial proposals.

---

## High-Level Architecture Diagram

```
+---------------------------------------------------------------------------------+
|                                USER INTERFACES                                  |
|   +------------------------------------+   +--------------------------------+   |
|   |  Streamlit Cloud Dashboard (:8501) |   |  React 18 + Vite SPA (:5173)   |   |
|   +------------------------------------+   +--------------------------------+   |
+----------------------------------------+----------------------------------------+
                                         | HTTP / REST
                                         v
+---------------------------------------------------------------------------------+
|                             FASTAPI BACKEND SERVICE (:8000)                     |
|  - /api/process (Background Workers)       - /api/catalog (FMCG SKU Query)      |
|  - /api/pricing/simulate (Margin Sandbox)  - /api/compliance/validate           |
|  - /api/rfp/{id}/export/pdf & excel        - /api/analytics (KPI Aggregator)    |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                      MULTI-AGENT ORCHESTRATION PIPELINE                         |
|                                                                                 |
|  +-------------------------+      +-------------------------------------------+ |
|  | 1. INTAKE AGENT         | ---> | 2. PACKAGING & UoM NORMALIZER             | |
|  | - PDF / TXT Parsing     |      | - Cartons, cases, dozens to retail units  | |
|  | - Metadata Extraction   |      +-------------------------------------------+ |
|  +-------------------------+                           |                        |
|                                                        v                        |
|  +-------------------------+      +-------------------------------------------+ |
|  | 4. PRICING AGENT        | <--- | 3. HYBRID SKU MATCHING AGENT              | |
|  | - Volume Tier Rebates   |      | - Semantic Vector Search (ChromaDB)       | |
|  | - GST Slabs (5/12/18%)  |      | - Token Overlap & Fuzzy Catalog Matcher   | |
|  +-------------------------+      +-------------------------------------------+ |
|               |                                                                 |
|               v                                                                 |
|  +-------------------------+      +-------------------------------------------+ |
|  | 5. COMPLIANCE CHECKER   | ---> | 6. SALES INSIGHTS AGENT                   | |
|  | - MOQ Verification      |      | - Win Probability Model (0-100%)          | |
|  | - Cold Chain Storage    |      | - SWOT Matrix & Deal Scorecard            | |
|  +-------------------------+      +-------------------------------------------+ |
|                                                        |                        |
|                                                        v                        |
|                                   +-------------------------------------------+ |
|                                   | 7. BEST PROPOSAL AGENT                    | |
|                                   | - Multi-Template Executive Quotations     | |
|                                   | - PDF & Excel Exporters                   | |
|                                   +-------------------------------------------+ |
+---------------------------------------------------------------------------------+
```

---

## Agent Responsibilities

### 1. Intake Agent (`rfp-automation/agents/intake_agent.py`)
- Accepts PDF or raw text files.
- Extracts retailer account name, delivery deadline, destination, and line item requirements.
- Flags non-FMCG inquiries automatically.

### 2. Packaging & UoM Normalizer (`rfp-automation/utils/uom_normalizer.py`)
- Translates wholesaler terminology ("10 cartons", "20 cases", "5 dozens") into standard consumer units based on category packaging specifications.

### 3. Hybrid SKU Matcher (`rfp-automation/agents/sku_matching_agent.py`)
- First searches vector embeddings in ChromaDB / Sentence-Transformers.
- Employs a deterministic token-overlap fallback matcher to guarantee zero dropped items.
- Returns matched SKU code, confidence score (0-100%), specifications, and justification.

### 4. Dynamic Pricing Engine (`rfp-automation/agents/pricing_agent.py`)
- Implements bracketed volume discount tiers (3% to 18%).
- Computes GST category rates (0% staples, 5% tea/dairy, 12% noodles/spreads, 18% personal/home care).
- Returns net taxable subtotal, CGST, SGST, volume savings, and grand total.

### 5. Compliance & Guardrails Checker (`rfp-automation/utils/compliance_checker.py`)
- Flags order quantities below manufacturer Minimum Order Quantities (MOQ).
- Automatically marks cold-chain logistics requirements for perishable dairy & edible oils.
- Evaluates minimum freight-free threshold requirements.

### 6. Sales Insights Agent (`rfp-automation/agents/sales_insight_agent.py`)
- Computes multi-factor win probability based on deal size, catalog coverage, margin, and SLAs.
- Generates competitive positioning strategies vs rival manufacturers (HUL, P&G, ITC, Nestlé, Dabur).
- Produces SWOT matrix and deal grade (A/B/C).

### 7. Proposal Agent (`rfp-automation/agents/best_proposal_agent.py`)
- Generates formal B2B sales proposals in Markdown, PDF, and Excel.
- Supports Executive, Standard, Wholesale Volume, and Express Restock templates.

---

## Performance & Reliability Patterns
- **Parallel Batching**: Line items are processed in parallel asynchronous batches using `asyncio.gather`.
- **Offline Simulation Mode**: The system includes deterministic mock agents for zero-API key execution.
- **Persistent LRU Cache**: Hashes prompts with SHA-256 to avoid duplicate LLM inferences.
