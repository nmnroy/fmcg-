from functools import lru_cache
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json

@lru_cache(maxsize=1)
def get_agents(use_mock=False):
    """Cache agent instances with lazy imports"""
    if use_mock:
        print("Initializing MOCK FMCG agents...")
        from agents.mock_agents import MockIntakeAgent, MockSKUMatchingAgent, MockPricingAgent, MockSalesInsightsAgent, MockBestProposalAgent
        return {
            'intake_process': MockIntakeAgent(),
            'sku_process': MockSKUMatchingAgent(),
            'pricing_process': MockPricingAgent(),
            'insights': MockSalesInsightsAgent(),
            'proposal': MockBestProposalAgent()
        }

    print("Initializing FMCG agents...")
    from agents.intake_agent import IntakeAgent
    from agents.sku_matching_agent import SKUMatchingAgent
    from agents.pricing_agent import PricingAgent
    from agents.sales_insight_agent import SalesInsightsAgent
    from agents.best_proposal_agent import BestProposalAgent
    
    return {
        'intake_process': IntakeAgent(),
        'sku_process': SKUMatchingAgent(),
        'pricing_process': PricingAgent(),
        'insights': SalesInsightsAgent(),
        'proposal': BestProposalAgent()
    }


async def process_rfp_async(rfp_path: str, simulation_mode: bool = False, progress_callback=None) -> Dict[str, Any]:
    """Process FMCG Order/RFP with detailed logging and safe fallbacks (Async)."""
    import asyncio
    
    def update_progress(stage: str, percent: int):
        if progress_callback:
            progress_callback(stage, percent)
        print(f"🔄 PROGRESS: {percent}% - {stage}")

    update_progress("File received", 5)

    print("\n" + "=" * 50)
    print(f" FMCG INTELLIGENT AGENT PROCESSING (Sim Mode: {simulation_mode}) [ASYNC]")
    print("=" * 50)

    start_time = time.time()
    agents = get_agents(use_mock=simulation_mode)

    # --- Read RFP/Order file safely (Blockng I/O in thread) ---
    update_progress("Parsing RFP text", 20)
    try:
        rfp_path_obj = Path(rfp_path)
        if not rfp_path_obj.is_file():
            raise FileNotFoundError(f"File not found: {rfp_path}")
        
        # Helper for file reading
        def read_file(path_obj):
            if path_obj.suffix.lower() == '.pdf':
                import PyPDF2
                with open(path_obj, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            else:
                with path_obj.open("r", encoding="utf-8") as f:
                    return f.read()

        rfp_text = await asyncio.to_thread(read_file, rfp_path_obj)
                
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return {
            "rfp_id": None,
            "error": f"Failed to read file: {e}",
        }

    rfp_id = f"ORDER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\n📋 Order ID: {rfp_id}")

    results: Dict[str, Any] = {}

    # --- Step 1: Intake (Extraction) ---
    update_progress("Extracting requirements", 40)
    print("📥 Step 1: Extracting Line Items...")
    agent_start = time.time()
    try:
        # Check if agent supports async, otherwise fallback
        if hasattr(agents['intake_process'], 'process_async'):
             rfp_data = await agents['intake_process'].process_async(rfp_text)
        else:
             rfp_data = await asyncio.to_thread(agents['intake_process'].process, rfp_text)
             
        if "error" in rfp_data:
             with open("main_error_log.txt", "a", encoding="utf-8") as f:
                f.write(f"INTAKE INNER ERROR: {rfp_data['error']}\n")
        
        results["rfp_data"] = rfp_data
        print(f"   ✅ Extracted {len(rfp_data.get('line_items', []))} items in {time.time() - agent_start:.1f}s")
    except Exception as e:
        print(f"   ❌ Intake failed: {e}")
        with open("main_error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"INTAKE ERROR: {e}\n")
        rfp_data = {"line_items": []}
        results["rfp_data"] = rfp_data

    # --- Step 2: SKU Matching ---
    update_progress("Matching SKUs (Parallel)", 65)
    print("🧠 Step 2: Matching SKUs...")
    agent_start = time.time()
    try:
        if hasattr(agents['sku_process'], 'process_async'):
             sku_matches = await agents['sku_process'].process_async(rfp_data)
        else:
             sku_matches = await asyncio.to_thread(agents['sku_process'].process, rfp_data)
             
        results["sku_matches"] = sku_matches
        print(f"   ✅ Matched items in {time.time() - agent_start:.1f}s")
    except Exception as e:
        print(f"   ❌ SKU Matching failed: {e}")
        sku_matches = {"matches": []}
        results["sku_matches"] = sku_matches

    # --- Step 3: Pricing ---
    update_progress("Pricing calculation", 80)
    print("💰 Step 3: Calculating Invoice...")
    agent_start = time.time()
    try:
        if hasattr(agents['pricing_process'], 'process_async'):
            pricing = await agents['pricing_process'].process_async(rfp_data, sku_matches)
        else:
            pricing = await asyncio.to_thread(agents['pricing_process'].process, rfp_data, sku_matches)
            
        results["pricing"] = pricing
        print(f"   ✅ Pricing done in {time.time() - agent_start:.1f}s")
    except Exception as e:
        print(f"   ❌ Pricing failed: {e}")
        results["pricing"] = {}

    # --- Step 4: Insights/Competitor ---
    update_progress("Analyzing market", 85)
    print("🔍 Step 4: Analyzing Competitors...")
    agent_start = time.time()
    try:
        if hasattr(agents['insights'], 'process_async'):
             insights = await agents['insights'].process_async(rfp_text, rfp_data, {}, results.get("pricing", {}))
        else:
             insights = await asyncio.to_thread(
                 agents['insights'].process, 
                 rfp_text, rfp_data, {}, results.get("pricing", {})
             )
        results["insights"] = insights
        print(f"   ✅ Analysis done in {time.time() - agent_start:.1f}s")
    except Exception as e:
        print(f"   ❌ Insights failed: {e}")
        results["insights"] = {}

    # --- Step 5: Proposal ---
    update_progress("Generating proposal", 95)
    print("📝 Step 5: Drafting Quote...")
    agent_start = time.time()
    try:
        if hasattr(agents['proposal'], 'process_async'):
             proposal = await agents['proposal'].process_async(
                 rfp_data, results.get("pricing", {}), results.get("insights", {})
             )
        else:
             proposal = await asyncio.to_thread(
                 agents['proposal'].process,
                 rfp_data, results.get("pricing", {}), results.get("insights", {})
             )
        results["proposal"] = proposal
        print(f"   ✅ Drafted in {time.time() - agent_start:.1f}s")
    except Exception as e:
        print(f"   ❌ Proposal failed: {e}")
        results["proposal"] = {"content": "Failed to generate."}

    # --- Save outputs (Async writes optional, keeping sync for safety) ---
    output_dir = Path("output") / rfp_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for key, data in results.items():
        if key == "proposal": continue
        try:
             # Fast sync write is fine
             (output_dir / f"{key}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        except: pass
        
    (output_dir / "proposal.md").write_text(results.get("proposal", {}).get("content", ""), encoding="utf-8")

    elapsed = time.time() - start_time
    print(f"\n⏱️  Total processing time: {elapsed:.1f} seconds")

    return {
        "rfp_id": rfp_id,
        "rfp_data": results.get("rfp_data"),
        "sku_matches": results.get("sku_matches"),
        "pricing": results.get("pricing"),
        "insights": results.get("insights"),
        "proposal": results.get("proposal"),
    }

def process_rfp(rfp_path: str, simulation_mode: bool = False, progress_callback=None) -> Dict[str, Any]:
    """Sync wrapper ensuring backward compatibility"""
    import asyncio
    try:
        return asyncio.run(process_rfp_async(rfp_path, simulation_mode, progress_callback))
    except Exception as e:
        print(f"CRITICAL ASYNC ERROR: {e}")
        # Fallback? No, just raise for now
        raise e

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python main.py <rfp_file_path>")
    else:
        # Run async version in script
        import asyncio
        asyncio.run(process_rfp_async(sys.argv[1]))