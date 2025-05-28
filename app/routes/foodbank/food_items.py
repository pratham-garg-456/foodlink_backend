from fastapi import APIRouter, HTTPException, Depends
from app.utils.jwt_handler import jwt_required
from app.services.foodbank.food_items_service import (
    get_food_items_in_db,
    add_a_food_item_in_db,
)

router = APIRouter()

# Route to add a food item to the database
@router.post("/food-item")
async def add_food_item(payload: dict = Depends(jwt_required), food_data: dict = {}):
    """
    Allow food bank admin to add a new food item to the inventory.
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param food_data: Food details including food_name, category, and unit.
    :return: A created food item is stored in the db.
    """
    # Validate if the request is made from a Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can add new food items to the inventory",
        )

    # Required keys in the body
    required_keys = ["food_name", "category", "unit", "expiration_date"]

    # Validate required fields
    for key in required_keys:
        if not food_data.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    # Add a new event in db
    food_item = await add_a_food_item_in_db(food_data=food_data)

    return {"status": "success", "food_item": food_item}


# Route to get food items from the database
@router.get("/food-items")
async def get_food_items(payload: dict = Depends(jwt_required)):
    """
    Allow food bank admin to retrieve food items from the inventory.
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :return: A list of food items from the inventory.
    """
    # Validate if the request is made from a Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can retrieve the food items from the inventory",
        )

    # Retrieve food items from the db
    food_items = await get_food_items_in_db()

    return {"status": "success", "food_items": food_items}