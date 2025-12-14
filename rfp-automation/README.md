# FMCG RFP Automation System

End-to-end agentic AI system for automating FMCG RFP (Request for Proposal) processing using LangGraph, LangChain, and local/vector tools.

## 1. Overview

Pipeline:
- **Agent 1 – Intake**: parse RFP, extract metadata + line items, classify and prioritize.
- **Agent 2 – SKU Matching**: semantic SKU search with sentence-transformers + ChromaDB.
- **Agent 3 – Pricing**: apply pricing rules, margins, discounts, approval flags.
- **Agent 4 – Proposal**: generate client-ready proposal in Markdown.
- **Agent 5 – Sales Insights**: win probability, risks, recommendations.
- **Agent 6 – Orchestrator (LangGraph)**: coordinates all agents and manages state.

Outputs per RFP:
- `output/<rfp_id>/intake.json`
- `output/<rfp_id>/sku_matches.json`
- `output/<rfp_id>/pricing.json`
- `output/<rfp_id>/insights.json`
- `output/<rfp_id>/proposal.md`

## 2. Installation

```bash
cd rfp-automation
python -m venv .venv
# Windows
.venv\\Scripts\\activate

pip install -r requirements.txt
```

## 3. Environment Configuration

Copy the example env and edit as needed:

```bash
cp .env.example .env
```

Set **one** of:
- `OPENAI_API_KEY` (and model)
- or `GROQ_API_KEY`
- or configure a local model via Ollama and adjust code to use it instead of `ChatOpenAI`.

## 4. Sample Data

- `data/sku_catalog.csv` – demo FMCG SKU catalog.
- `data/pricing_rules.json` – example margin and discount rules.
- `data/rfp_uploads/` – place your RFP PDFs/text files here.

## 5. Running a Test

Quick sanity check using the synthetic sample RFP:

```bash
cd rfp-automation
python test.py
```

This will:
- Create `data/rfp_uploads/sample_rfp.txt` if missing.
- Run the full LangGraph pipeline.
- Write all outputs under `output/<rfp_id>/`.

## 6. Running on Your Own RFP

```bash
cd rfp-automation
python main.py path/to/your_rfp.pdf
# or
python main.py path/to/your_rfp.txt
```

Results will be written under `output/<rfp_id>/`.

## 7. Architecture Diagram (ASCII)

```text
           +-------------------+
           |  RFP PDF / Text  |
           +---------+---------+
                     |
                     v
             utils/pdf_parser.py
                     |
                     v
              +--------------+
              |  Orchestrator|
              |  (LangGraph) |
              +------+-------+
                     |
     ---------------------------------------------
     |            |           |         |        |
     v            v           v         v        v
 +--------+   +-------+   +--------+ +--------+ +---------+
 |Intake  |   | SKU   |   |Pricing | |Proposal| |Insights |
 |Agent   |   |Agent  |   |Agent   | |Agent   | |Agent    |
 +--------+   +-------+   +--------+ +--------+ +---------+
     |            |           |         |        |
     ---------------------------------------------
                     |
                     v
              +--------------+
              |  output/<id> |
              +--------------+
```

## 8. Troubleshooting

- **LLM errors / bad JSON**
  - Check `.env` and API keys.
  - Reduce temperature to `0` (already default).
  - Log raw LLM output where needed.

- **No SKU matches / low confidence**
  - Verify `data/sku_catalog.csv` contents.
  - Recreate embeddings by deleting `chroma_db/` and rerunning.

- **Pricing looks off**
  - Review `data/pricing_rules.json`.
  - Confirm quantities in intake output are parsed correctly.

- **Pipeline crashes**
  - Inspect `errors` array in final state (printed by `test.py`).
  - Run individual agents in isolation if needed.

## 9. Next Steps / Extensibility

- Swap `ChatOpenAI` with Groq or local models.
- Add new agents (e.g., legal / compliance review).
- Add a simple FastAPI/Streamlit UI around `process_rfp()`.
