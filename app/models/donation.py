from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Literal

class Donation(Document):
    donor_id: str  # Reference to a user (donor)
    amount: float
    status: Literal["pending", "confirmed", "failed"] = "pending"
    foodbank_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        collection = "donations"
