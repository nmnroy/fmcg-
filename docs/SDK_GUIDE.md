# FMCG Python SDK & CLI Developer Guide

## 1. Overview
The FMCG Intelligent RFP Suite provides both an intuitive Command Line Interface (`cli.py`) and a typed Python SDK (`sdk/fmcg_client.py`) for automated quote processing and ERP/distributor integrations.

---

## 2. CLI Usage

### Process an Order File
Process raw customer purchase orders or tenders into structured commercial quotations:
```bash
python3 cli.py process data/sample_supermarket_monthly_restock.txt --mock --pdf quotes/quote.pdf --csv quotes/quote.csv
```

### Search the Master SKU Catalog
```bash
python3 cli.py catalog -q "Tea" -n 10
python3 cli.py catalog -c "Beverages"
```

### Run System Audit
```bash
python3 cli.py verify
```

---

## 3. Python SDK Usage

### Initialize the Client
```python
from sdk.fmcg_client import FMCGClient

client = FMCGClient(base_url="http://localhost:8000")
```

### Check Service Health
```python
health = client.check_health()
print(f"Server status: {health['status']}, Catalog SKUs: {health['catalog_size']}")
```

### Search Catalog
```python
results = client.search_catalog(query="Basmati Rice", limit=5)
for item in results.get("items", []):
    print(item["sku_id"], item["sku_name"], item["base_price"])
```

### Simulate GST & Volume Tier Pricing
```python
quote = client.simulate_pricing(sku_id="SKU-STA-001", quantity=250, discount_pct=5.0)
print("Base:", quote["base_total_inr"])
print("Volume Discount:", quote["volume_discount_pct"])
print("GST:", quote["gst_amount"])
print("Payable:", quote["final_payable_inr"])
```

---

## 4. Make Targets
A complete Makefile is provided for convenience:
```bash
make test         # Run all unit tests
make audit        # Run end-to-end integration audit
make benchmark    # Benchmark latency and throughput
make run-backend  # Start FastAPI server
make run-streamlit# Start Streamlit UI
```
