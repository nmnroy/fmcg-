import sys
import os
import csv
import json
import shutil
import uuid
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse, Response
import uvicorn

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
RFP_DIR = BASE_DIR / "rfp-automation"
if str(RFP_DIR) not in sys.path:
    sys.path.append(str(RFP_DIR))

# Import Agents & Utilities
from main import process_rfp
from utils.gemini_wrapper import GeminiLLM
from utils.pdf_generator import generate_rfp_pdf
from utils.excel_exporter import export_rfp_to_csv
from utils.compliance_checker import validate_order_compliance
from models import (
    ChatRequest, CatalogItem, CatalogResponse,
    PricingSimulationRequest, PricingSimulationResponse,
    ProcessTextRequest, AnalyticsSummary
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FMCG-API")

app = FastAPI(
    title="FMCG Agentic AI Enterprise API",
    version="3.5.0",
    description="RESTful API for automated FMCG RFP processing, SKU matching, dynamic pricing, and proposal generation."
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Job & History In-Memory Store
jobs: Dict[str, Dict[str, Any]] = {}

def get_history_file() -> Path:
    p = BASE_DIR / "data" / "rfp_history.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def load_rfp_history() -> List[Dict[str, Any]]:
    h_file = get_history_file()
    if h_file.exists():
        try:
            with open(h_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_rfp_history(entry: Dict[str, Any]):
    h_file = get_history_file()
    history = load_rfp_history()
    history.insert(0, entry)
    with open(h_file, "w", encoding="utf-8") as f:
        json.dump(history[:50], f, indent=2)

def load_catalog_data() -> List[Dict[str, Any]]:
    candidates = [
        BASE_DIR / "data" / "sku_catalog.csv",
        BASE_DIR / "rfp-automation" / "data" / "sku_catalog.csv"
    ]
    for p in candidates:
        if p.exists():
            items = []
            with open(p, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    items.append({
                        "sku_id": r.get("sku_id", ""),
                        "name": r.get("name", ""),
                        "category": r.get("category", "General"),
                        "specs": r.get("specs", ""),
                        "base_cost": float(r.get("base_cost", 0.0) or 0.0),
                        "unit": r.get("unit", "units"),
                        "gst_pct": float(r.get("gst_pct", 18.0) or 18.0),
                        "pack_size": r.get("pack_size", "standard")
                    })
            return items
    return []

@app.get("/")
def health_check():
    return RedirectResponse(url="/docs")

@app.get("/api/health")
def api_health():
    catalog = load_catalog_data()
    return {
        "status": "healthy",
        "service": "FMCG Agentic AI API",
        "version": "3.5.0",
        "catalog_items_loaded": len(catalog),
        "active_jobs": len(jobs)
    }

# --- Catalog Endpoints ---
@app.get("/api/catalog", response_model=CatalogResponse)
def get_catalog(
    category: Optional[str] = Query(None, description="Filter by category"),
    q: Optional[str] = Query(None, description="Search query")
):
    """Retrieve and search master FMCG SKU catalog"""
    items = load_catalog_data()
    categories = sorted(list({i["category"] for i in items}))
    
    filtered = items
    if category and category != "All":
        filtered = [i for i in filtered if i["category"].lower() == category.lower()]
    if q:
        query = q.lower()
        filtered = [i for i in filtered if query in i["name"].lower() or query in i["sku_id"].lower() or query in i["specs"].lower()]

    catalog_items = [CatalogItem(**it) for it in filtered]
    return CatalogResponse(total=len(catalog_items), categories=categories, items=catalog_items)

@app.get("/api/catalog/{sku_id}", response_model=CatalogItem)
def get_catalog_item(sku_id: str):
    """Retrieve specific SKU details by SKU ID"""
    items = load_catalog_data()
    for item in items:
        if item["sku_id"].lower() == sku_id.lower():
            return CatalogItem(**item)
    raise HTTPException(status_code=404, detail="SKU ID not found in catalog")

# --- Pricing Simulation Endpoint ---
@app.post("/api/pricing/simulate", response_model=PricingSimulationResponse)
def simulate_pricing(req: PricingSimulationRequest):
    """Interactive commercial quote and margin simulator"""
    running_gross = 0.0
    running_taxable = 0.0
    running_gst = 0.0
    processed_items = []

    margin_multiplier = 1.0 / (1.0 - (req.margin_pct / 100.0)) if req.margin_pct < 100 else 1.0

    for item in req.items:
        base_cost = item.base_cost
        sell_unit_price = round(base_cost * margin_multiplier, 2)
        line_taxable = round(sell_unit_price * item.quantity, 2)
        gst_pct = item.gst_pct or 18.0
        line_gst = round(line_taxable * (gst_pct / 100.0), 2)
        line_total = round(line_taxable + line_gst, 2)

        running_gross += round(base_cost * item.quantity, 2)
        running_taxable += line_taxable
        running_gst += line_gst

        processed_items.append({
            "sku_name": item.sku_name,
            "quantity": item.quantity,
            "unit_cost": base_cost,
            "sell_unit_price": sell_unit_price,
            "gst_pct": gst_pct,
            "line_taxable": line_taxable,
            "line_gst": line_gst,
            "line_total": line_total
        })

    grand_total = round(running_taxable + running_gst, 2)
    discount = 0.0

    return PricingSimulationResponse(
        gross_total=running_gross,
        discount_amount=discount,
        taxable_subtotal=running_taxable,
        gst_amount=running_gst,
        grand_total=grand_total,
        margin_pct=req.margin_pct,
        items=processed_items
    )

# --- Background Job Management ---
def run_processing_task(job_id: str, file_path: str, simulation_mode: bool = False):
    try:
        def callback(stage, percent):
            if job_id in jobs:
                jobs[job_id]["progress"] = percent
                jobs[job_id]["stage"] = stage

        jobs[job_id]["status"] = "processing"
        result = process_rfp(file_path, simulation_mode=simulation_mode, progress_callback=callback)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["stage"] = "Completed"
        jobs[job_id]["result"] = result

        # Save to history
        save_rfp_history({
            "id": result.get("rfp_id", job_id),
            "filename": Path(file_path).name,
            "date": Path(file_path).stat().st_mtime,
            "value": result.get("pricing", {}).get("summary", {}).get("grand_total", 0.0),
            "file_path": str(file_path),
            "result": result
        })

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

@app.post("/api/process")
async def process_rfp_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    simulation_mode: bool = Query(False, description="Use offline simulation mode")
):
    """Upload and start processing an RFP file in the background"""
    try:
        logger.info(f"Processing file: {file.filename} (Sim: {simulation_mode})")
        upload_dir = BASE_DIR / "data" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "progress": 0,
            "stage": "File received",
            "result": None
        }

        background_tasks.add_task(run_processing_task, job_id, str(file_path), simulation_mode)
        return {"job_id": job_id, "message": "Processing started", "simulation_mode": simulation_mode}

    except Exception as e:
        logger.error(f"Error processing RFP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-text")
async def process_text_endpoint(background_tasks: BackgroundTasks, req: ProcessTextRequest):
    """Process raw text RFP or Purchase Order directly"""
    try:
        upload_dir = BASE_DIR / "data" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"text_{int(uuid.uuid4().hex[:8])}.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(req.text)

        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "progress": 0,
            "stage": "Text received",
            "result": None
        }

        background_tasks.add_task(run_processing_task, job_id, str(file_path), req.simulation_mode)
        return {"job_id": job_id, "message": "Processing started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status/{job_id}")
async def get_job_status(job_id: str):
    """Get status of an ongoing processing job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

# --- Chat Endpoint ---
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Interactive AI Assistant for RFP consultation"""
    try:
        llm = GeminiLLM()
        system_instruction = f"You are an FMCG Expert Sales & Procurement Assistant.\nContext:\n{req.context}"
        response = llm.generate_content(req.message, system_instruction=system_instruction)
        return {"response": response}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"response": f"Assistant ready in offline mode. Context noted for item queries."}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
