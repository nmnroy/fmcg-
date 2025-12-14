import sys
import os
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

# Add rfp-automation directly to path
# We assume this file is in /backend and rfp-automation is in /rfp-automation (sibling)
BASE_DIR = Path(__file__).resolve().parent.parent
RFP_DIR = BASE_DIR / "rfp-automation"
sys.path.append(str(RFP_DIR))

# Import Agents
from main import process_rfp
from utils.gemini_wrapper import GeminiLLM

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FMCG-API")

app = FastAPI(title="FMCG Agentic AI API", version="3.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class ChatRequest(BaseModel):
    message: str
    context: str = ""

# --- Endpoints ---

from fastapi.responses import RedirectResponse

@app.get("/")
def health_check():
    return RedirectResponse(url="/docs")

# --- Job Management ---
jobs = {}

class JobStatus(BaseModel):
    job_id: str
    status: str  # processing, completed, failed
    progress: int
    stage: str
    result: dict = None
    error: str = None

from fastapi import BackgroundTasks
import uuid
import threading

def run_processing_task(job_id: str, file_path: str):
    """Background task wrapper"""
    try:
        def callback(stage, percent):
            jobs[job_id]["progress"] = percent
            jobs[job_id]["stage"] = stage
        
        jobs[job_id]["status"] = "processing"
        result = process_rfp(file_path, progress_callback=callback)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["stage"] = "Completed"
        jobs[job_id]["result"] = result
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

@app.post("/api/process")
async def process_rfp_endpoint(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload and start processing an RFP file"""
    try:
        logger.info(f"Processing file: {file.filename}")
        
        # Save temp file
        upload_dir = BASE_DIR / "data" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Create Job
        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "progress": 0,
            "stage": "File received",
            "result": None
        }
        
        # Start Background Task
        background_tasks.add_task(run_processing_task, job_id, str(file_path))
        
        return {"job_id": job_id, "message": "Processing started"}

    except Exception as e:
        logger.error(f"Error processing RFP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a processing job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Chat with the AI Assistant"""
    try:
        llm = GeminiLLM()
        # Combine context and message
        system_instruction = f"You are an FMCG Expert Assistant.\nReference Data:\n{req.context}"
        response = llm.generate_content(req.message, system_instruction=system_instruction)
        return {"response": response}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
