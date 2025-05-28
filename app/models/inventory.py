from beanie import Document
from pydantic import BaseModel
from typing import List
from datetime import datetime, timezone
from pydantic import Field

class MainInventoryFoodItem(BaseModel):
    food_name: str
    quantity: float


class MainInventory(Document):
    stock: List[MainInventoryFoodItem]
    foodbank_id: str
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        collection = "inventory"