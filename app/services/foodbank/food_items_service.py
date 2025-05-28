from app.models.food_item import FoodItem
from fastapi import HTTPException
from app.utils.time_converter import convert_string_time_to_iso
from datetime import datetime, timezone

async def add_a_food_item_in_db(food_data: dict):
    """
    Add a food item to the database.
    :param food_data: A dictionary containing food item data, including the expiration date, food name, category, etc.
    """
    # Check if a food item with the same name already exists in the database
    existing_food_item = await FoodItem.find_one(
        FoodItem.food_name == food_data["food_name"]
    )
    if existing_food_item:
        raise HTTPException(
            status_code=400,
            detail="A food item with the same name already exists in the database.",
        )

    # Parse expiration_date if it exists, otherwise set it to None
    expiration_date = None
    if food_data.get("expiration_date"):
        expiration_date = convert_string_time_to_iso(
            food_data["expiration_date"].split(" ")[0],
            food_data["expiration_date"].split(" ")[1],
        )

    try:
        # Create a new FoodItem instance
        new_food_item = FoodItem(
            food_name=food_data["food_name"],
            category=food_data["category"],
            unit=food_data["unit"],
            description=food_data.get("description"),
            expiration_date=expiration_date,
            added_on=datetime.now(timezone.utc),
        )

        # Insert the new food item into the database
        await new_food_item.insert()
        new_food_item = new_food_item.model_dump()
        new_food_item["id"] = str(new_food_item.get("id"))

        return new_food_item

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while adding the food item to the database: {e}",
        )


async def get_food_items_in_db():
    """
    Retrieve a list of food items from the database for a specific food bank.
    :param foodbank_id: A unique identifier for the food bank.
    """
    food_items_list = []

    try:
        # Retrieve the food items related to the specific food bank
        food_items = await FoodItem.find().to_list()

        for food_item in food_items:
            food_item_dict = food_item.model_dump()
            food_item_dict["id"] = str(
                food_item_dict["id"]
            )  # Convert MongoDB ObjectId to string
            food_items_list.append(food_item_dict)

        return food_items_list

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while fetching the list of food items in db: {e}",
        )