from app.models.user import User
from beanie import PydanticObjectId
from typing import List
from fastapi import HTTPException
from datetime import datetime, timezone

async def update_details_information(
    id: str,
    desc: str,
    location: str,
    operating_hours: str,
    services: List[str],
    phone_number: str,
    image_url: str,
):
    """
    update detailed information of a foodbank in db
    :param id: A mongoDB identifier
    :param description: A brief description about foodbank
    :param location: An address of foodbank
    :param operating_hours: Operating Hours of a foodbank
    :param services: List of offered services
    :param image_url: Profile picture
    :param phone_number: Foodbank office phone number
    """

    try:
        foodbank = await User.get(PydanticObjectId(id))

        if not foodbank:
            raise HTTPException(status_code=404, detail="User not found!")

        if foodbank.role != "foodbank":
            raise HTTPException(status_code=400, detail="User is not a foodbank admin")
        foodbank.description = desc
        foodbank.location = location
        foodbank.operating_hours = operating_hours

        # Empty the services before appending new one
        foodbank.services_offered = []
        for service in services:
            foodbank.services_offered.append(service)

        foodbank.updated_at = datetime.now(timezone.utc)
        foodbank.phone_number = phone_number
        foodbank.image_url = image_url

        await foodbank.save()
        foodbank = foodbank.model_dump()
        foodbank["id"] = str(foodbank["id"])

        return foodbank

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating the metadata for foodbank: {e}",
        )
