"""
FMCG API Client SDK
High-level programmatic Python client for FMCG RFP Processing & Catalog querying.
"""

from typing import Dict, Any, List, Optional
import urllib.request
import urllib.parse
import json


class FMCGClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        if params:
            url += f"?{urllib.parse.urlencode(params)}"

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        req_data = json.dumps(data).encode("utf-8") if data else None

        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e), "success": False}

    def check_health(self) -> Dict[str, Any]:
        """Check server health and loaded SKU catalog size."""
        return self._request("GET", "/health")

    def search_catalog(self, query: str = "", category: str = "", limit: int = 50) -> Dict[str, Any]:
        """Search catalog by query or category."""
        params = {}
        if query:
            params["q"] = query
        if category:
            params["category"] = category
        if limit:
            params["limit"] = limit
        return self._request("GET", "/catalog", params=params)

    def simulate_pricing(self, sku_id: str, quantity: float, discount_pct: float = 0.0) -> Dict[str, Any]:
        """Simulate real-time GST and volume-tiered commercial pricing for a SKU."""
        payload = {
            "sku_id": sku_id,
            "quantity": quantity,
            "custom_discount_pct": discount_pct
        }
        return self._request("POST", "/pricing/simulate", data=payload)

    def verify_compliance(self, line_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify cold-chain compliance and packaging integrity."""
        payload = {"line_items": line_items}
        return self._request("POST", "/compliance/verify", data=payload)

    def get_analytics(self) -> Dict[str, Any]:
        """Fetch sales analytics KPIs and order metrics."""
        return self._request("GET", "/analytics/kpis")
