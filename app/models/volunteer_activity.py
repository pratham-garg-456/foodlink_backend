from beanie import Document
from datetime import datetime
from pydantic import BaseModel


class WorkingHours(BaseModel):
    start: datetime
    end: datetime


class VolunteerActivity(Document):
    application_id: str
    date_worked: datetime
    foodbank_name: str
    category: str
    working_hours: WorkingHours

    class Settings:
        collection = "volunteer_activities"
