from beanie import Document
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing_extensions import Literal
from pydantic import Field
from datetime import timezone
from typing import List

class EventInventoryFoodItem(BaseModel):
    food_name: str
    quantity: float

class EventInventory(Document):
    stock: List[EventInventoryFoodItem]
    event_id: str  # Reference to Event
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Event(Document):
    foodbank_id: str
    event_name: str
    description: str
    date: datetime
    start_time: datetime
    end_time: datetime
    location: str
    status: Literal["scheduled", "ongoing", "completed", "cancelled"] = "scheduled"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        collection = "events"
        
