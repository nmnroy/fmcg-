# 🛒 FMCG Agentic AI — Intelligent RFP & Order Response Platform

[![CI/CD](https://github.com/nmnroy/fmcg-/actions/workflows/ci.yml/badge.svg)](https://github.com/nmnroy/fmcg-/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-3.5.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg?logo=streamlit)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**FMCG Agentic AI** is an enterprise autonomous system designed to transform how FMCG manufacturers, wholesale distributors, and retail procurement teams respond to Requests for Proposal (RFPs), purchase orders, and store replenishment requests. Powered by multi-agent LLM orchestration, hybrid semantic RAG, and deterministic commercial pricing rules. 🚀

📎 **Live Streamlit App:** [https://fmcgagenticai.streamlit.app/](https://fmcgagenticai.streamlit.app/)  
🎬 **Demo Video:** [Google Drive Walkthrough](https://drive.google.com/drive/folders/1uK4Kx7LA3BpVCvavCjc1nMCvc8VS8fNX?usp=sharing)

---

## 🌟 Key Capabilities & Features

| Capability | Description |
|:---|:---|
| 📥 **Multimodal Intake** | Ingests purchase orders from messy unstructured PDFs, scanned files, or raw text. |
| 📦 **Packaging & UoM Normalizer** | Translates wholesaler terminology (*cartons, cases, dozens, gross*) into standard consumer retail units. |
| 🧠 **Hybrid SKU Matching Engine** | Combines ChromaDB vector semantic search with deterministic token-overlap fallback to guarantee zero dropped items. |
| 💰 **Dynamic Commercial Pricing** | Bracketed volume discount tiers (3% to 18%), category-specific GST slabs (5%, 12%, 18%), and distributor margin simulation. |
| 🛡️ **Procurement Guardrails** | Automated MOQ verification, cold-chain logistics flags, and minimum order threshold checks. |
| 🔍 **Sales Insights & SWOT** | Multi-factor win probability scoring (0–100%), SWOT matrix generation, and competitive counter-strategies vs rival brands. |
| 📄 **Document Generation** | Instant generation of branded ReportLab PDF quotes, multi-tab Excel/CSV spreadsheets, and formatted Markdown proposals. |
| 🌐 **Dual UI & REST API** | Full Streamlit web application + modern React 18 / Tailwind SPA powered by a FastAPI backend. |
| ⚡ **Offline Simulation Mode** | Zero-API key demo mode with high-fidelity mock agents for instant offline evaluation. |

---

## 🏗️ Architecture & Multi-Agent Flow

```
                      +-----------------------------+
                      |   Unstructured RFP / Order  |
                      |     (PDF, TXT, or JSON)     |
                      +--------------+--------------+
                                     |
                                     v
                       +---------------------------+
                       |    1. Intake Agent        |
                       | - Account metadata        |
                       | - Delivery deadlines      |
                       +-------------+-------------+
                                     |
                                     v
                       +---------------------------+
                       | 2. Packaging Normalizer   |
                       | - Cartons -> Retail Units |
                       | - Dozens -> Units         |
                       +-------------+-------------+
                                     |
                                     v
                       +---------------------------+
                       | 3. Hybrid SKU Matcher     |
                       | - Vector embeddings (RAG) |
                       | - Fuzzy catalog fallback  |
                       +-------------+-------------+
                                     |
                                     v
                       +---------------------------+
                       |  4. Pricing Engine        |
                       | - Volume discount tiers   |
                       | - Category GST slabs      |
                       +-------------+-------------+
                                     |
                                     v
                       +---------------------------+
                       | 5. Compliance Guardrails  |
                       | - MOQ verification       |
                       | - Cold-chain flags        |
                       +-------------+-------------+
                                     |
                                     v
                       +---------------------------+
                       | 6. Sales Insights Agent   |
                       | - Win probability (0-100%)|
                       | - SWOT & deal grade       |
                       +-------------+-------------+
                                     |
                                     v
                       +---------------------------+
                       | 7. Proposal Agent         |
                       | - PDF Invoice             |
                       | - Excel / CSV Export      |
                       +---------------------------+
```

---

## 🗂 Repository Structure

```
├── .github/workflows/ci.yml       # Automated GitHub Actions CI pipeline
├── backend/                       # Enterprise FastAPI REST service
│   ├── server.py                  # API endpoints (Catalog, Pricing, Export, Analytics)
│   ├── models.py                  # Pydantic v2 data schemas
│   └── test_endpoints.py          # Starlette TestClient integration test suite
├── frontend/                      # React 18 + Vite + Tailwind CSS frontend
│   ├── src/components/            # Dashboard, CatalogTab, AnalyticsTab, ProposalTab
│   └── src/lib/api.ts             # Typed API client library
├── rfp-automation/                # Multi-Agent Intelligence Core
│   ├── agents/                    # Intake, SKU Matching, Pricing, Insights, Proposal
│   ├── utils/                     # Normalizer, PDF Generator, Excel Exporter, Cache
│   └── data/                      # 100+ Master SKU catalog & pricing rules
├── data/                          # Shared catalogs, pricing rules & sample orders
├── tests/                         # Comprehensive unit tests (19+ test cases)
├── docs/                          # Architecture documentation & API references
├── streamlit_app.py               # Live Streamlit application entry point
├── generate_pdf.py                # Standalone PDF quotation generation CLI
├── verify_system.py               # End-to-end system verification audit script
├── docker-compose.yml             # Full-stack multi-container orchestration
└── Dockerfile                     # Production container image
```

---

## 🚀 Quick Start

### Option 1: Run with Python

```bash
# Clone the repository
git clone https://github.com/nmnroy/fmcg-.git
cd fmcg-

# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# (Optional) Configure Gemini API Key in .env
echo "GOOGLE_API_KEY=your_key_here" > .env

# Run System Verification Audit
python verify_system.py

# Launch Streamlit Web Application
streamlit run streamlit_app.py
```

### Option 2: Run FastAPI Backend & React Frontend

```bash
# Terminal 1: Launch FastAPI Backend
uvicorn backend.server:app --reload --port 8000

# Terminal 2: Launch React Frontend
cd frontend
npm install
npm run dev
```

### Option 3: Run with Docker Compose

```bash
docker-compose up --build
```
- **Streamlit App:** `http://localhost:8501`
- **FastAPI Documentation:** `http://localhost:8000/docs`
- **React Dashboard:** `http://localhost:5173`

---

## 🧪 Running Automated Tests

```bash
# Run unit test suite
python -m unittest discover tests

# Run backend API integration tests
python -m unittest backend/test_endpoints.py

# Run comprehensive system verification
python verify_system.py
```

---

## 📦 Master SKU Catalog

The platform includes over 100+ active enterprise FMCG SKUs spanning:
- **Personal Care**: Shampoos (Dove, Sunsilk, Tresemme), Soaps (Lux, Lifebuoy, Pears), Lotions (Vaseline), Creams (Ponds), Hair Oils (Parachute, Dabur Amla).
- **Home Care**: Detergent Powders & Liquids (Surf Excel, Rin), Dishwash (Vim), Floor Cleaners (Domex), Insecticides (HIT).
- **Packaged Foods**: Instant Noodles (Maggi, YiPPee), Biscuits (Good Day, Marie Gold, Dark Fantasy), Sauces (Kissan), Jams.
- **Beverages**: Tea (Tata Tea, Red Label, Taj Mahal), Coffee (Bru, Nescafe), Juices (Real, B Natural).
- **Dairy & Staples**: Cow Ghee (Aashirvaad, Amul), Butter (Amul), Atta (Aashirvaad), Salt (Tata Salt).
- **Oral Care**: Toothpastes (Colgate, Closeup, Dabur Red, Meswak), Toothbrushes, Mouthwash.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
