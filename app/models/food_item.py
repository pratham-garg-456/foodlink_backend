from datetime import datetime, timezone
from typing import Optional, Literal
from pydantic import Field
from beanie import Document

class FoodItem(Document):
    food_name: str
    category: Literal[
        "Vegetables", "Fruits", "Dairy", "Meat", 
        "Canned Goods", "Grains", "Beverages", "Snacks","Packed Food", "Others"
    ]  # Restricts input to only these categories
    
    unit: Literal["kg", "grams", "liters", "ml", "pcs", "packs"]  # Restricts input to valid units
    description: Optional[str] = None
    expiration_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    added_on: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        collection = "food_items"
