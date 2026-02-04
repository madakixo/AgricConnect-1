from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ListingCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    category_id: int
    price_per_unit: float = Field(..., gt=0)
    unit: str = Field(..., pattern="^(kg|bag|basket|tonne|piece|litre)$")
    quantity_available: float = Field(..., gt=0)
    market_name: Optional[str] = None
    harvest_date: Optional[datetime] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class ListingOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category_id: int
    price_per_unit: float
    unit: str
    quantity_available: float
    market_name: Optional[str]
    images: List[str]
    harvest_date: Optional[datetime]
    # Add lat/lon or distance if needed later

    class Config:
        from_attributes = True
