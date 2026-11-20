# FMCG Agentic AI REST API Reference

Base URL: `http://localhost:8000/api`

---

## 1. System Health
### `GET /api/health`
Returns backend service status, catalog counts, and active worker count.

**Response:**
```json
{
  "status": "healthy",
  "service": "FMCG Agentic AI API",
  "version": "3.5.0",
  "catalog_items_loaded": 101,
  "active_jobs": 0
}
```

---

## 2. Catalog Management
### `GET /api/catalog`
Search and filter master SKU catalog.

**Query Parameters:**
- `category` (optional, string): e.g. `Personal Care`, `Home Care`, `Beverages`
- `q` (optional, string): search keyword across name, brand, or SKU ID

**Response:**
```json
{
  "total": 101,
  "categories": ["Beverages", "Dairy & Staples", "Home Care", "Oral Care", "Packaged Foods", "Personal Care"],
  "items": [
    {
      "sku_id": "HUL_DOVE_001",
      "name": "Dove Hair Fall Rescue Shampoo 340ml",
      "category": "Personal Care",
      "specs": "volume:340ml,variant:hair_fall,brand:Dove",
      "base_cost": 250.0,
      "unit": "bottle",
      "gst_pct": 18.0,
      "pack_size": "340ml"
    }
  ]
}
```

### `GET /api/catalog/{sku_id}`
Retrieve individual SKU metadata by ID.

---

## 3. Commercial Pricing Simulation
### `POST /api/pricing/simulate`
Simulates quote totals with custom margin percentages.

**Request Body:**
```json
{
  "margin_pct": 20.0,
  "items": [
    {
      "sku_name": "Dove Shampoo 340ml",
      "quantity": 100,
      "base_cost": 250.0,
      "category": "Personal Care",
      "gst_pct": 18.0
    }
  ]
}
```

**Response:**
```json
{
  "gross_total": 25000.0,
  "discount_amount": 0.0,
  "taxable_subtotal": 31250.0,
  "gst_amount": 5625.0,
  "grand_total": 36875.0,
  "margin_pct": 20.0,
  "items": [...]
}
```

---

## 4. Order Compliance
### `POST /api/compliance/validate`
Validates orders against distributor business policies (MOQs, cold chain, minimum value).

---

## 5. RFP Processing
### `POST /api/process`
Upload an RFP file (`.pdf` or `.txt`) for background processing.

**Query Parameters:**
- `simulation_mode` (boolean): `true` for offline zero-API key execution.

### `GET /api/status/{job_id}`
Polls processing stage (0-100%) and returns completed result.

---

## 6. Document Exports
### `GET /api/rfp/{rfp_id}/export/pdf`
Streams the generated quotation as an official ReportLab PDF.

### `GET /api/rfp/{rfp_id}/export/excel`
Streams quotation line items and financial summary as a CSV/Excel spreadsheet.

---

## 7. Analytics & History
### `GET /api/analytics`
Returns aggregate pipeline value, average win probability, category distributions, and top SKUs.

### `GET /api/history`
Lists past processed RFP documents with pagination and keyword filtering.

### `DELETE /api/history/{rfp_id}`
Removes an order entry from history.
