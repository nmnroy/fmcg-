"""
Pydantic Models and Data Contracts for FMCG Backend API
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or message")
    context: str = Field("", description="RFP context string or JSON")


class CatalogItem(BaseModel):
    sku_id: str
    name: str
    category: str
    specs: str
    base_cost: float
    unit: str
    gst_pct: float = 18.0
    pack_size: Optional[str] = "standard"


class CatalogResponse(BaseModel):
    total: int
    categories: List[str]
    items: List[CatalogItem]


class SimulationItem(BaseModel):
    sku_name: str
    quantity: int = Field(gt=0, default=10)
    base_cost: float = Field(gt=0, default=100.0)
    category: str = "Personal Care"
    gst_pct: Optional[float] = 18.0


class PricingSimulationRequest(BaseModel):
    margin_pct: float = Field(ge=0, le=90, default=20.0)
    items: List[SimulationItem]


class PricingSimulationResponse(BaseModel):
    gross_total: float
    discount_amount: float
    taxable_subtotal: float
    gst_amount: float
    grand_total: float
    margin_pct: float
    items: List[Dict[str, Any]]


class AnalyticsSummary(BaseModel):
    total_rfps_processed: int
    pipeline_value_inr: float
    avg_win_rate_pct: float
    active_rfps_count: int
    category_distribution: Dict[str, int]
    top_demanded_skus: List[Dict[str, Any]]


class ProcessTextRequest(BaseModel):
    text: str = Field(..., description="Raw RFP text / order content")
    client_name: Optional[str] = "Retail Partner"
    simulation_mode: bool = False
