import sys
import os
import json

# Add rfp-automation to path
sys.path.append(os.path.join(os.getcwd(), 'rfp-automation'))

from main import process_rfp

if __name__ == "__main__":
    file_path = "sample_fmcg_hypermarket_order.txt"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
        
    print(f"Running pipeline on {file_path}")
    try:
        result = process_rfp(file_path)
        print("\n--- FINAL RESULT SUMMARY ---")
        items = result.get('rfp_data', {}).get('line_items', [])
        print(f"Line Items: {len(items)}")
        print(json.dumps(result.get('rfp_data', {}), indent=2))
    except Exception as e:
        print(f"CRITICAL FAILURE: {e}")
        with open("last_error.txt", "w", encoding="utf-8") as f:
            f.write(str(e))
            import traceback
            f.write("\n")
            traceback.print_exc(file=f)
