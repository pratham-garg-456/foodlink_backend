from fastapi import APIRouter, HTTPException, Depends
from app.utils.jwt_handler import jwt_required
from app.services.foodbank.inventory_service import (
    add_inventory_in_db,
    get_inventory_in_db,
    remove_inventory_in_db,
)

router = APIRouter()


@router.post("/inventory")
async def add_inventory(
    payload: dict = Depends(jwt_required), inventory_data: dict = {}
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
    print(type(inventory_data["stock"][0]["quantity"]))
    if inventory_data is None:
        raise HTTPException(
            status_code=400,
            detail="Inventory data is required",
        )

    # Validate each item in the stock list
    for item in inventory_data["stock"]:
        # Convert given quantity to float type
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
    new_inventory = await add_inventory_in_db(
        payload.get("sub"),
        inventory_data["stock"],
    )

    return {"status": "success", "inventory": new_inventory}


@router.put("/inventory")
async def update_inventory(
    payload: dict = Depends(jwt_required),
    updated_inventory: dict = {},
):
    """
    Allow food bank admin to update inventory by either adding or removing quantities.
    :param inventory_id: A unique number to identify the correct inventory item.
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param updated_inventory: the updated inventory data (including food_name and quantity).
    :return: Updated inventory items stored in the db.
    """
    # Validate if the request is made from Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401, detail="Only FoodBank admin can update the inventory"
        )

    # Iterate over the list of items and handle quantity changes (remove or add)
    for food_item in updated_inventory["stock"]:
        food_name = food_item.get("food_name")
        quantity = food_item.get("quantity")

        # Check that food_name and quantity are provided for each item
        if not food_name or not quantity:
            raise HTTPException(
                status_code=400, detail="Each item must contain food_name and quantity"
            )

        # Call the appropriate function to update/remove inventory
        updated_food = await remove_inventory_in_db(
            payload.get("sub"), updated_inventory["stock"]
        )

    return {"status": "success", "inventory": updated_food}


@router.get("/inventory")
async def get_inventory(payload: dict = Depends(jwt_required)):
    """
    Allow food bank admin to retrieve inventory
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :return: A list inventory item is stored in the db
    """

    # Validate if the request is made from Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can retrieve the inventory list",
        )

    inventory_list = await get_inventory_in_db(foodbank_id=payload.get("sub"))

    return {"status": "success", "inventory": inventory_list}
