from app.models.donation import Donation
from fastapi import HTTPException
from app.models.user import User
from datetime import datetime, timezone
from beanie import PydanticObjectId
from app.models.event import Event, EventInventory


async def create_donation_in_db(donor_id: str, donation_data: dict):
    """
    Allow a donor to make a monetary donation.
    :param donor_id: The ID of the donor making the donation.
    :param donation_data: Dict containing donation details (e.g., "amount").
    :return: Donation details as a dict.
    """
    try:
        new_donation = Donation(
            donor_id=donor_id,
            amount=donation_data["amount"],
            foodbank_id=donation_data["foodbank_id"],
            status="confirmed",
        )
        await new_donation.insert()
        donation = new_donation.model_dump()
        donation["id"] = str(donation["id"])
        return donation
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error creating donation in db: {str(e)}"
        )


async def get_donations_by_user(donor_id: str):
    """
    Retrieve all donations made by a specific donor.
    :param donor_id: The ID of the donor.
    :return: A list of donation details.
    """
    donation_list = []
    try:
        donations = await Donation.find(Donation.donor_id == donor_id).to_list()
        for donation in donations:
            donation = donation.model_dump()
            donation["id"] = str(donation["id"])
            
            # Get donor 
            donation_list.append(donation)
        return donation_list
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving donations for user {donor_id}: {str(e)}",
        )


async def update_donor_detailed_info_in_db(
    id: str, desc: str, image_url: str, phone_number: str
):
    """
    update metadata for donor users in db
    :param id: A mongoDB identifier
    :param description: A brief description about donor
    :param image_url: Profile Image
    :param phone_number: donor's Phone Number
    """
    try:
        donor = await User.get(PydanticObjectId(id))

        if not donor:
            raise HTTPException(status_code=404, detail="User not found!")

        if donor.role != "donor":
            raise HTTPException(status_code=400, detail="User is not a donor")

        donor.description = desc
        donor.image_url = image_url
        donor.phone_number = phone_number
        donor.updated_at = datetime.now(timezone.utc)

        await donor.save()
        donor = donor.model_dump()
        donor["id"] = str(donor["id"])

        return donor

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating the metadata for donor: {e}",
        )


async def retrieve_list_of_events_in_db():
    """
    Retrieve the detailed information about an ongoing events
    """
    # Initialize the list with empty array
    event_list = []
    try:
        events = await Event.find().to_list()

        for event in events:
            event = event.model_dump()
            event["id"] = str(event["id"])

            # Fetch event inventory
            event_inventory = await EventInventory.find_one(
                EventInventory.event_id == event["id"]
            )
            if not event_inventory:
                raise HTTPException(
                    status_code=404, detail="Event inventory not found."
                )

            event_inventory = event_inventory.model_dump()
            event_inventory["id"] = str(event_inventory["id"])

            event["event_inventory"] = event_inventory
            event_list.append(event)

        return event_list
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching the list of events: {e}",
        )
