from fastapi import HTTPException
from app.models.inventory import MainInventory, MainInventoryFoodItem
from app.models.food_item import FoodItem
from typing import List
from datetime import datetime, timezone


async def add_inventory_in_db(foodbank_id: str, inventory_data: List[dict]):
    """
    Add or update inventory for specific food names and quantities.
    :param foodbank_id: The ID of the foodbank where inventory will be stored.
    :param inventory_data: List of dictionaries containing food items with their names and quantities.
    :return: List of added or updated inventory items.
    """

    added_inventory = []

    try:
        # Iterate over the inventory data (list of food items and their quantities)
        for food in inventory_data:
            food_name = food["food_name"]
            quantity = food["quantity"]

            # Check if the food item already exists in the FoodItem collection.
            existing_food_item = await FoodItem.find_one(
                FoodItem.food_name == food_name
            )

            # If the food item doesn't exist, raise an exception
            if not existing_food_item:
                raise HTTPException(
                    status_code=404,
                    detail=f"The food item '{food_name}' does not exist in the database. Please add the food item first.",
                )

            # Ensure 'unit' exists
            unit = existing_food_item.unit  # Set default to 'unknown' if not provided
            expiration_date = existing_food_item.expiration_date

            # If the food item exists, check if the foodbank's inventory exists.
            existing_inventory = await MainInventory.find_one(
                MainInventory.foodbank_id == foodbank_id
            )

            if existing_inventory:
                # If the food item already exists in the stock, update its quantity
                food_found = False
                for item in existing_inventory.stock:
                    if item.food_name == food_name:
                        item.quantity += quantity  # Update the quantity
                        food_found = True
                        break

                if not food_found:
                    # If the food item is not found in stock, append the new item to the stock array
                    new_food_item = MainInventoryFoodItem(
                        food_name=food_name, quantity=quantity
                    )
                    existing_inventory.stock.append(new_food_item)

                # Update the `last_updated` timestamp
                existing_inventory.last_updated = datetime.now(timezone.utc)

                # Save the updated MainInventory record
                await existing_inventory.save()

                # Return the updated inventory
                existing_inventory = existing_inventory.model_dump()
                existing_inventory["id"] = str(existing_inventory["id"])
                added_inventory.append(
                    {
                        "food_name": food_name,
                        "quantity": quantity,
                        "foodbank_id": foodbank_id,
                        "expiration_date": expiration_date,
                        "unit": unit,
                        "updated_on": existing_inventory["last_updated"].isoformat(),
                    }
                )

            else:
                # If no existing inventory for the foodbank, create a new MainInventory
                new_inventory_item = MainInventory(
                    foodbank_id=foodbank_id,
                    stock=[
                        MainInventoryFoodItem(food_name=food_name, quantity=quantity)
                    ],
                    last_updated=datetime.now(timezone.utc),
                )
                # Insert the new inventory into the database
                await new_inventory_item.insert()

                # Return the new inventory item with its id
                new_inventory_item = new_inventory_item.model_dump()
                new_inventory_item["id"] = str(new_inventory_item["id"])
                added_inventory.append(
                    {
                        "food_name": food_name,
                        "quantity": quantity,
                        "foodbank_id": foodbank_id,
                        "expiration_date": expiration_date,
                        "unit": unit,
                        "added_on": new_inventory_item["last_updated"],
                    }
                )

        return added_inventory  # Return the list of added or updated inventory items

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while adding or updating inventory: {str(e)}",
        )


async def remove_inventory_in_db(foodbank_id: str, inventory_data: List[dict]):
    """
    Remove the inventory for specific food names and quantities in the given foodbank.
    :param foodbank_id: The ID of the foodbank where inventory will be updated.
    :param inventory_data: List of dictionaries containing food items with their names and quantities to be removed.
    :return: List of removed inventory items.
    """

    removed_inventory = []  # List to store removed inventory items

    try:
        # Iterate over the inventory data (list of food items and their quantities)
        for food in inventory_data:
            food_name = food["food_name"]
            quantity = food["quantity"]

            # Check if the food item exists in the FoodItem collection.
            existing_food_item = await FoodItem.find_one(
                FoodItem.food_name == food_name
            )

            # If the food item doesn't exist, raise an exception
            if not existing_food_item:
                raise HTTPException(
                    status_code=404,
                    detail=f"The food item '{food_name}' does not exist in the database. Please add the food item first.",
                )

            # Ensure 'unit' and 'expiration_date' are available
            unit = existing_food_item.unit  # Default to 'unknown' if not provided
            expiration_date = existing_food_item.expiration_date

            # If the food item exists, check if the foodbank's inventory exists.
            existing_inventory = await MainInventory.find_one(
                MainInventory.foodbank_id == foodbank_id
            )

            if existing_inventory:
                food_found = False
                for item in existing_inventory.stock:
                    if item.food_name == food_name:
                        if item.quantity >= quantity:
                            # If quantity to remove is less than or equal to what's available, subtract it
                            item.quantity -= quantity
                            if item.quantity == 0:
                                # Remove the food item completely if quantity reaches 0
                                existing_inventory.stock.remove(item)
                            food_found = True
                        else:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Not enough quantity of '{food_name}' in inventory to remove.",
                            )
                        break

                if not food_found:
                    # If the food item doesn't exist in stock, return an error
                    raise HTTPException(
                        status_code=404,
                        detail=f"The food item '{food_name}' does not exist in the inventory for the given foodbank.",
                    )

                # Update the `last_updated` timestamp
                existing_inventory.last_updated = datetime.now(timezone.utc)

                # Save the updated MainInventory record
                await existing_inventory.save()

                # Return the removed inventory information
                existing_inventory = existing_inventory.model_dump()
                existing_inventory["id"] = str(existing_inventory["id"])
                removed_inventory.append(
                    {
                        "food_name": food_name,
                        "quantity_removed": quantity,
                        "foodbank_id": foodbank_id,
                        "expiration_date": expiration_date,
                        "unit": unit,
                        "updated_on": existing_inventory["last_updated"].isoformat(),
                    }
                )
            else:
                # If no existing inventory for the foodbank, return an error
                raise HTTPException(
                    status_code=404,
                    detail=f"No inventory found for foodbank '{foodbank_id}'.",
                )

        return removed_inventory  # Return the list of removed inventory items

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while removing inventory: {str(e)}",
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

        return inventory_list  # Return the list of inventories

    except Exception as e:
        # Handle any errors that occur while retrieving the inventory
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving the inventory for foodbank '{foodbank_id}': {str(e)}",
        )
