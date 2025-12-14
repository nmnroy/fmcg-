"""Simple test script for the RFP Automation System."""

import os
from pathlib import Path
from main import process_rfp


def create_sample_rfp(path: Path) -> None:
    sample_text = """Company Name: Global Foods Inc.
RFP Title: Q4 2024 Beverage & Grocery Supply Contract
Deadline: 12/15/2024
Estimated Value: $50,000

Requirements:
1. Premium Tea Bags 100ct - 500 boxes
2. Instant Coffee 200g - 300 jars
3. Cooking Oil 1L refined - 1000 bottles
4. Wheat Flour 1kg - 2000 packets
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sample_text, encoding="utf-8")


def main() -> None:
    base = Path(__file__).parent
    rfp_path = base / "data" / "rfp_uploads" / "sample_rfp.txt"

    if not rfp_path.exists():
        print("Creating sample RFP text file...")
        create_sample_rfp(rfp_path)

    print(f"Processing sample RFP: {rfp_path}")
    final_state = process_rfp(str(rfp_path))

    rfp_id = final_state.get("rfp_id", "RFP_UNKNOWN")
    output_dir = base / "output" / rfp_id

    print("\nSummary:")
    print(f"RFP ID: {rfp_id}")
    print(f"Output directory: {output_dir}")
    print(f"Status: {final_state.get('status')}")
    print(f"Errors: {final_state.get('errors')}")

    # Basic validation of outputs
    expected_files = [
        "intake.json",
        "sku_matches.json",
        "pricing.json",
        "insights.json",
        "proposal.md",
    ]
    missing = [f for f in expected_files if not (output_dir / f).exists()]
    if missing:
        print("Missing output files:", missing)
    else:
        print("All expected output files generated.")


if __name__ == "__main__":
    main()
