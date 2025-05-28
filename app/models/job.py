from beanie import Document
from datetime import datetime, timezone
import pytz
from typing import Literal


class Job(Document):
    foodbank_id: str
    title: str
    description: str
    location: str
    category: str
    date_posted: datetime = datetime.now(timezone.utc)
    deadline: datetime
    status: Literal["available", "unavailable"] = "available"

    class Settings:
        collection = "jobs"

    async def check_and_update_status(self):
        # Convert deadline datetime obj to offset-aware timezone
        utc = pytz.UTC
        deadline = utc.localize(self.deadline)
        if deadline <= datetime.now(timezone.utc) and self.status != "unavailable":
            self.status = "unavailable"
            await self.save()


class EventJob(Job):
    event_id: str

    class Settings:
        collection = "event_jobs"
