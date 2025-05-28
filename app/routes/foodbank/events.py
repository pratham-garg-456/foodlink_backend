from fastapi import APIRouter, HTTPException, Depends
from app.utils.jwt_handler import jwt_required
from app.services.foodbank.event_service import (
    create_an_event_in_db,
    get_list_of_events,
    update_the_existing_event_in_db,
    delete_event_in_db,
    add_event_inventory_to_db,
    update_event_inventory_in_db,
    transfer_event_inventory_to_main_inventory_in_db,
    get_event_inventory_from_db,
)

router = APIRouter()


@router.post("/event")
async def create_an_event(payload: dict = Depends(jwt_required), event_data: dict = {}):
    """
    Allow food bank admin to create an event
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param event_data: A detailed event including name, optional description, date, start_time, end_time, location, list of food services, and event inventory
    :return A created event is stored in the db
    """
    # Validate if the request is made from Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401, detail="Only FoodBank admin can create an event"
        )

    # Required key in the body
    required_key = [
        "event_name",
        "description",
        "date",
        "start_time",
        "end_time",
        "location",
    ]

    # Start validation those keys
    for key in required_key:
        if not event_data.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    # Add a new event in db
    event = await create_an_event_in_db(
        foodbank_id=payload.get("sub"), event_data=event_data
    )

    return {"status": "success", "event": event}


@router.get("/events")
async def get_list_of_event(payload: dict = Depends(jwt_required)):
    """
    Allow foodbank admin to retrieve the list of events
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :return a list of events
    """
    # Validate if the request is made from Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can retrieve the list of events",
        )

    # Retrieve events from db
    events = await get_list_of_events(foodbank_id=payload.get("sub"))

    if len(events) == 0:
        raise HTTPException(
            status_code=404,
            detail="There are no events here!",
        )

    return {"status": "success", "events": events}


@router.put("/event/{event_id}")
async def update_an_existing_event(
    event_id: str, payload: dict = Depends(jwt_required), updated_event: dict = {}
):
    """
    Allow foodbank admin to update an existing event
    :param event_id: A unique identifier for event to retrieve the correct event from db
    :param payload: Decoded JWT containing user claims (validated via jwt_required)
    :return an updated event
    """

    # Validate if the request is made from Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401, detail="Only FoodBank admin can update an event"
        )

    # Required key in the body
    required_key = [
        "event_name",
        "date",
        "start_time",
        "end_time",
        "location",
    ]

    # Start validation those keys
    for key in required_key:
        if not updated_event.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    updated_event = await update_the_existing_event_in_db(
        event_id=event_id, event_data=updated_event
    )

    return {"status": "success", "event": updated_event}


@router.delete("/event/{event_id}")
async def delete_event(event_id: str, payload: dict = Depends(jwt_required)):
    """
    Allow foodbank admin to delete an event
    :param event_id: A unique identifier for event
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    """
    # Validate if the request is made from Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can delete an event",
        )

    await delete_event_in_db(event_id=event_id)

    return {"status": "success", "detail": "The event is removed from the database!"}


@router.get("/event/{event_id}/inventory")
async def get_event_inventory_route(event_id: str):
    """
    Get the inventory of a specific event.
    :param event_id: The ID of the event to fetch the inventory for.
    :return: A list of items in the event's inventory.
    """
    try:
        event_inventory = await get_event_inventory_from_db(event_id)
        return event_inventory
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/event/{event_id}/inventory")
async def add_inventory_to_event(
    event_id: str, payload: dict = Depends(jwt_required), inventory_data: dict = {}
):
    """
    Allow food bank admin to add inventory
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param inventory_data: Inventory details including food_name and quantity
    :return: A created inventory item is stored in the db
    """
    # Validate if the request is made from Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can add new food in the main inventory",
        )
    # If no inventory data is provided
    if inventory_data is None:
        raise HTTPException(
            status_code=400,
            detail="Inventory data is required",
        )

    # Validate each item in the stock list
    for item in inventory_data["stock"]:
        if item["quantity"] != None:
            item["quantity"] = float(item["quantity"])
            
        if "food_name" not in item or not item["food_name"]:
            raise HTTPException(
                status_code=400,
                detail="Each inventory item must have a non-empty 'food_name'",
            )
        if (
            "quantity" not in item
            or not isinstance(item["quantity"], float)
            or item["quantity"] <= 0
        ):
            raise HTTPException(
                status_code=400,
                detail="Each inventory item must have a valid 'quantity' (positive value)",
            )

    # Store the new food in the db
    new_inventory = await add_event_inventory_to_db(
        event_id,
        payload.get("sub"),
        inventory_data["stock"],
    )

    return {"status": "success", "inventory": new_inventory}


@router.put("/event/{event_id}/inventory")
async def add_inventory_to_event(
    event_id: str, payload: dict = Depends(jwt_required), inventory_data: dict = {}
):
    """
    Allow food bank admin to add inventory
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param inventory_data: Inventory details including food_name and quantity
    :return: A created inventory item is stored in the db
    """
    # Validate if the request is made from Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can add new food in the main inventory",
        )
    # If no inventory data is provided
    if inventory_data is None:
        raise HTTPException(
            status_code=400,
            detail="Inventory data is required",
        )

    # Validate each item in the stock list
    for item in inventory_data["stock"]:
        if item["quantity"] != None:
            item["quantity"] = float(item["quantity"])

        if "food_name" not in item or not item["food_name"]:
            raise HTTPException(
                status_code=400,
                detail="Each inventory item must have a non-empty 'food_name'",
            )
        if (
            "quantity" not in item
            or not isinstance(item["quantity"], float)
            or item["quantity"] <= 0
        ):
            raise HTTPException(
                status_code=400,
                detail="Each inventory item must have a valid 'quantity' (positive value)",
            )

    # Store the new food in the db
    new_inventory = await update_event_inventory_in_db(
        event_id,
        inventory_data["stock"],
    )

    return {"status": "success", "inventory": new_inventory}


@router.put("/event/{event_id}/inventory/transfer-back")
async def transfer_back_to_main_inventory_route(
    event_id: str,
    payload: dict = Depends(jwt_required),
):
    """
    Route for transferring remaining items from event inventory back to main inventory.
    :param event_id: The ID of the event from which to transfer items.
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :return: The updated main inventory after transferring items.
    """
    # Validate if the request is made from a Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401, detail="Only FoodBank admin can transfer inventory"
        )

    # Transfer items back to main inventory
    try:
        inventory = await transfer_event_inventory_to_main_inventory_in_db(
            payload.get("sub"), event_id=event_id
        )

        return {"status": "success", "inventory": inventory}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while transferring inventory: {str(e)}",
        )
