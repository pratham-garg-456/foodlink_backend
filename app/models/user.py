from beanie import Document
from datetime import datetime, timezone
from typing import Literal, Optional, List


class User(Document):
    name: str
    role: Literal["foodbank", "individual", "donor", "volunteer"]
    email: str
    password: str
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    experiences: Optional[str] = None
    
    description: Optional[str] = None
    location: Optional[str] = None
    operating_hours: Optional[str] = None
    services_offered: Optional[List[str]] = []
    phone_number: Optional[str] = None

    image_url: Optional[str] = None
    
    class Settings:
        collection = "users"


# class Volunteer(User):
#     # Additional fields for volunteers
#     experiences: Optional[str] = None
#     description: Optional[str] = None
