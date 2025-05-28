from fastapi import HTTPException
from beanie import PydanticObjectId
from datetime import datetime, timezone
from app.utils.time_converter import convert_string_time_to_iso
from app.models.event import Event, EventInventory, EventInventoryFoodItem
from typing import List
from app.models.inventory import MainInventory


async def create_an_event_in_db(foodbank_id: str, event_data: dict):
    """
    Create an event for upcoming events
    :param event_data: A detailed event including name, optional description, date, start_time, end_time, location, list of food services, and event MainInventory
    """    
    try:
        # Convert datetime fields
        date = convert_string_time_to_iso(event_data["date"], event_data["start_time"])

        start = convert_string_time_to_iso(event_data["date"], event_data["start_time"])

        end = convert_string_time_to_iso(event_data["date"], event_data["end_time"])
        
        event_data["date"] = date
        event_data["start_time"] = start
        event_data["end_time"] = end
        
        # Create the event
        new_event = Event(
            foodbank_id=foodbank_id,
            event_name=event_data["event_name"],
            description=event_data["description"],
            date=event_data["date"],
            start_time=event_data["start_time"],
            end_time=event_data["end_time"],
            location=event_data["location"],
            status=event_data["status"],
        )
        await new_event.insert()
        new_event = new_event.model_dump()
        new_event["id"] = str(new_event["id"])
        return new_event

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(ve)}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating an event in db: {str(e)}",
        )


async def get_list_of_events(foodbank_id: str):
    """
    Retrieve a list of events in db
    :param foodbank_id: A unique identifier for Foodbank admin
    """

    event_list = []

    events = await Event.find(Event.foodbank_id == foodbank_id).to_list()

    try:
        for event in events:
            event = event.model_dump()
            event["id"] = str(event["id"])
            event["start_time"] = str(event["start_time"]) + "Z"
            event["end_time"] = str(event["end_time"]) + "Z"
            event_list.append(event)

        return event_list
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while fetching the list of events in db: {e}",
        )


async def update_the_existing_event_in_db(event_id: str, event_data: dict):
    """
    Update an existing event in db
    :param event_id: An event ID
    :param event_data: An updated event data
    """

    event = await Event.get(PydanticObjectId(event_id))

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Convert datetime fields
    date = convert_string_time_to_iso(event_data["date"], event_data["start_time"])

    start = convert_string_time_to_iso(event_data["date"], event_data["start_time"])

    end = convert_string_time_to_iso(event_data["date"], event_data["end_time"])

    event_data["date"] = date
    event_data["start_time"] = start
    event_data["end_time"] = end

    # Update the exisitng event in db
    try:
        for key, value in event_data.items():
            setattr(event, key, value)
        # Update the modification date
        event.last_updated = datetime.now(timezone.utc)
        await event.save()
        event = event.model_dump()
        event["id"] = str(event["id"])
        return event
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while updating the event in db: {e}",
        )


async def delete_event_in_db(event_id: str):
    """
    Delete the existing event based on the requested ID
    :param event_id: An unique identifier of event
    """
    event = await Event.get(PydanticObjectId(event_id))

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    try:
        await event.delete()
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"An error occurred while deleting the event"
        )


async def get_event_inventory_from_db(event_id: str):
    """
    Retrieve the inventory for a specific event.
    :param event_id: ID of the event.
    :return: List of items in the EventInventory.
    """
    try:
        # Fetch event inventory
        event_inventory = await EventInventory.find_one(
            EventInventory.event_id == event_id
        )

        if not event_inventory:
            raise HTTPException(status_code=404, detail="Event inventory not found.")

        event_inventory = event_inventory.model_dump()
        event_inventory["id"] = str(event_inventory["id"])
        return {"status": "success", "event_inventory": event_inventory}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving event inventory: {str(e)}"
        )


async def add_event_inventory_to_db(
    event_id: str, foodbank_id: str, stock_data: List[dict]
):
    """
    Add items from MainInventory to EventInventory for a specific event.
    :param event_id: ID of the event where inventory is added.
    :param foodbank_id: ID of the food bank.
    :param stock_data: List of food items to add.
    :return: Updated EventInventory
    """
    try:
        # Fetch the main inventory for the food bank
        main_inventory = await MainInventory.find_one(
            MainInventory.foodbank_id == foodbank_id
        )
        if not main_inventory or not main_inventory.stock:
            raise HTTPException(
                status_code=404,
                detail=f"Main inventory not found or empty for food bank ID: {foodbank_id}.",
            )
        # Check if the event exists
        event = await Event.get(PydanticObjectId(event_id))
        if not event:
            raise HTTPException(
                status_code=404, detail=f"Event not found for ID: {event_id}."
            )

        # check if event Inventory exist for the event
        event_inventory = await EventInventory.find_one(
            EventInventory.event_id == event_id
        )
        if not event_inventory:
            event_inventory = EventInventory(stock=[], event_id=event_id)
            await event_inventory.insert()

        # Process each item
        for item in stock_data:
            food_name = item["food_name"]
            quantity = item["quantity"]

            # Check if food item exists in MainInventory
            food_item_found = False
            for mi_item in main_inventory.stock:
                if mi_item.food_name == food_name:
                    print(f"Found food item: {food_name}")
                    if mi_item.quantity < quantity:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Not enough quantity of '{food_name}' in MainInventory.",
                        )
                    # Deduct quantity from MainInventory
                    mi_item.quantity -= quantity
                    if mi_item.quantity == 0:
                        main_inventory.stock.remove(mi_item)
                    food_item_found = True
                    break

            if not food_item_found:
                raise HTTPException(
                    status_code=404,
                    detail=f"The food item '{food_name}' does not exist in MainInventory.",
                )

            # Check if item already exists in EventInventory
            event_food_found = False
            for ei_item in event_inventory.stock:
                if ei_item.food_name == food_name:
                    ei_item.quantity += quantity
                    event_food_found = True
                    break

            if not event_food_found:
                # Add a new item if it does not exist
                event_inventory.stock.append(
                    EventInventoryFoodItem(food_name=food_name, quantity=quantity)
                )

        # Update timestamps
        main_inventory.last_updated = datetime.now(timezone.utc)
        event_inventory.last_updated = datetime.now(timezone.utc)

        # Save changes
        await main_inventory.save()
        await event_inventory.save()
        main_inventory = main_inventory.model_dump()
        event_inventory = event_inventory.model_dump()
        main_inventory["id"] = str(main_inventory["id"])
        event_inventory["id"] = str(event_inventory["id"])

        return event_inventory

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while adding inventory to event: {str(e)}",
        )


async def update_event_inventory_in_db(event_id: str, used_items: List[dict]):
    """
    Update EventInventory when items are used.
    :param event_id: ID of the event.
    :param used_items: List of items with updated quantities.
    :return: Updated EventInventory
    """
    try:
        # Fetch event inventory
        event_inventory = await EventInventory.find_one(
            EventInventory.event_id == event_id
        )
        if not event_inventory:
            raise HTTPException(status_code=404, detail="Event inventory not found.")

        # Update quantities
        for used_item in used_items:
            event_item = next(
                (
                    ei
                    for ei in event_inventory.stock
                    if ei.food_name == used_item["food_name"]
                ),
                None,
            )
            if not event_item or event_item.quantity < used_item["quantity"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough '{used_item.food_name}' in EventInventory.",
                )

            event_item.quantity -= used_item["quantity"]
            if event_item.quantity == 0:
                event_inventory.stock.remove(event_item)

        event_inventory.last_updated = datetime.now(timezone.utc)
        await event_inventory.save()
        event_inventory = event_inventory.model_dump()
        event_inventory["id"] = str(event_inventory["id"])

        return event_inventory

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating event inventory in db: {str(e)}"
        )


async def transfer_event_inventory_to_main_inventory_in_db(
    foodbank_id: str, event_id: str
):
    """
    Transfer remaining items from EventInventory back to MainInventory.
    :param event_id: ID of the event.
    :param foodbank_id: ID of the food bank.
    :return: Updated MainInventory
    """
    try:
        # Fetch event inventory
        event_inventory = await EventInventory.find_one(
            EventInventory.event_id == event_id
        )
        if not event_inventory or not event_inventory.stock:
            raise HTTPException(
                status_code=404, detail="No inventory to transfer back."
            )

        # Fetch main inventory for the food bank
        main_inventory = await MainInventory.find_one(
            MainInventory.foodbank_id == foodbank_id
        )
        if not main_inventory:
            main_inventory = MainInventory(foodbank_id=foodbank_id, stock=[])

        # Transfer items back
        for item in event_inventory.stock:
            main_item = next(
                (mi for mi in main_inventory.stock if mi.food_name == item.food_name),
                None,
            )
            if main_item:
                main_item.quantity += item.quantity
            else:
                main_inventory.stock.append(item)

        # Clear event inventory
        event_inventory.stock = []
        event_inventory.last_updated = datetime.now(timezone.utc)
        main_inventory.last_updated = datetime.now(timezone.utc)

        await event_inventory.save()
        await main_inventory.save()
        main_inventory = main_inventory.model_dump()
        event_inventory = event_inventory.model_dump()
        main_inventory["id"] = str(main_inventory["id"])
        event_inventory["id"] = str(event_inventory["id"])

        return main_inventory

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error transferring inventory back: {str(e)}"
        )
