from app.models.appointment import Appointment
from fastapi import HTTPException
from app.models.inventory import MainInventory
from datetime import datetime, timezone
from app.models.user import User
from datetime import datetime, timezone
from beanie import PydanticObjectId
from app.models.event import Event, EventInventory


async def create_appointment_in_db(individual_id: str, appointment_data: dict):
    """
    Add an appointment in db and reserve inventory items.
    :param individual_id: ID of the individual making the appointment
    :param appointment_data: A detailed appointment information
    """

    try:
        # Fetch food bank inventory
        foodbank_id = appointment_data["foodbank_id"]
        existing_inventory = await MainInventory.find_one(
            MainInventory.foodbank_id == foodbank_id
        )

        if not existing_inventory:
            raise HTTPException(
                status_code=404, detail="No inventory found for this food bank."
            )

        # Check if requested items are available and update inventory
        for item in appointment_data["product"]:
            food_name = item["food_name"]
            quantity_requested = item["quantity"]

            food_found = False
            for stock_item in existing_inventory.stock:
                if stock_item.food_name == food_name:
                    if stock_item.quantity >= quantity_requested:
                        stock_item.quantity -= (
                            quantity_requested  # Deduct quantity (Reserve)
                        )
                        food_found = True
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Not enough stock for {food_name}. Available: {stock_item.quantity}, Requested: {quantity_requested}",
                        )
                    break

            if not food_found:
                raise HTTPException(
                    status_code=404,
                    detail=f"{food_name} is not available in this food bank's inventory.",
                )

        # Save updated inventory
        existing_inventory.last_updated = datetime.now(timezone.utc)
        await existing_inventory.save()

        # Create the appointment after reserving inventory
        new_appointment = Appointment(
            individual_id=individual_id,
            foodbank_id=foodbank_id,
            start_time=appointment_data["start_time"],
            end_time=appointment_data["end_time"],
            description=appointment_data.get("description", None),
            product=appointment_data["product"],
        )

        await new_appointment.insert()
        new_appointment = new_appointment.model_dump()
        new_appointment["id"] = str(new_appointment["id"])

        return new_appointment

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while creating an appointment: {e}",
        )


async def get_appointments_by_individual(individual_id: str):
    """
    Fetch all appointments for a specific food bank.

    :param foodbank_id: The ID of the food bank.
    :return: A list of appointment objects.
    """
    try:
        appointments = await Appointment.find(
            Appointment.individual_id == individual_id
        ).to_list()

        # Convert ObjectId to string for JSON response
        for appointment in appointments:
            appointment = appointment.model_dump()
            appointment["id"] = str(appointment["id"])

        return appointments

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching appointments for individual: {str(e)}",
        )


async def get_inventory_in_db(foodbank_id: str):
    """
    Retrieve the list of MainInventory for a specific foodbank in db.
    :param foodbank_id: The ID of the food bank
    :return: List of inventories for the given foodbank.
    """
    inventory_list = []

    try:
        # Find all MainInventory entries for the given foodbank_id
        main_inventory = await MainInventory.find(
            MainInventory.foodbank_id == foodbank_id
        ).to_list()

        # If no inventory found, return a clear message
        if not main_inventory:
            raise HTTPException(
                status_code=404,
                detail=f"No inventory found for foodbank '{foodbank_id}'.",
            )

        # Process each inventory item
        for inv in main_inventory:
            # Convert the inventory item to a dictionary
            inv_data = inv.model_dump()
            inv_data["id"] = str(inv_data["id"])  # Ensure ID is a string
            inventory_list.append(inv_data)

        return inventory_list[0]  # Return the list of inventories

    except Exception as e:
        # Handle any errors that occur while retrieving the inventory
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving the inventory for foodbank '{foodbank_id}': {str(e)}",
        )


async def update_individual_detailed_info_in_db(
    id: str, desc: str, image_url: str, phone_number: str
):
    """
    update metadata for individual users in db
    :param id: A mongoDB identifier
    :param description: A brief description about individual
    :param image_url: Profile Image
    :param phone_number: individual's Phone Number
    """
    try:
        individual = await User.get(PydanticObjectId(id))

        if not individual:
            raise HTTPException(status_code=404, detail="User not found!")

        if individual.role != "individual":
            raise HTTPException(status_code=400, detail="User is not a individual")

        individual.description = desc
        individual.image_url = image_url
        individual.phone_number = phone_number
        individual.updated_at = datetime.now(timezone.utc)

        await individual.save()
        individual = individual.model_dump()
        individual["id"] = str(individual["id"])

        return individual

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating the metadata for individual: {e}",
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
