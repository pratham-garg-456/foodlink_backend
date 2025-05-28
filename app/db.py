from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import (
    user,
    service,
    contact,
    event,
    inventory,
    application,
    appointment,
    donation,
    job,
    food_item,
)
from app.config import settings
from app.models import volunteer_activity


async def init_db():
    """
    Initialize the MongoDB database with Beanie models.
    """
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client.get_database("FoodLink-Collection")
    await init_beanie(
        database=db,
        document_models=[
            user.User,
            service.Service,
            contact.Contact,
            event.Event,
            event.EventInventory,
            inventory.MainInventory,
            application.Application,
            appointment.Appointment,
            donation.Donation,
            job.Job,
            volunteer_activity.VolunteerActivity,
            food_item.FoodItem,
        ],
    )
