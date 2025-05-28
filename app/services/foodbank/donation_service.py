from app.models.donation import Donation
from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId


async def get_all_donations(foodbank_id: str):

    donation_list = []

    """
    Retrieve all donation records from the database.
    :return: List of donations.
    """
    try:
        donations = await Donation.find(Donation.foodbank_id == foodbank_id).to_list()
        for donation in donations:
            donation = donation.model_dump()
            donation["id"] = str(donation["id"])
            donation_list.append(donation)

        return donation_list
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while retrieving a list of donations in db: {str(e)}",
        )


async def search_donations(
    foodbank_id: str,
    donor_id: Optional[str] = None,
    donation_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    status: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
) -> List[Donation]:
    query = {"foodbank_id": foodbank_id}

    if donor_id:
        query["donor_id"] = donor_id
    if donation_id:
        try:
            donation_id = PydanticObjectId(donation_id)
            query["_id"] = donation_id
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid donation_id: {str(e)}"
            )
    if start_time:
        query["created_at"] = {"$gte": start_time}
    if end_time:
        if "created_at" in query:
            query["created_at"]["$lte"] = end_time
        else:
            query["created_at"] = {"$lte": end_time}
    if status:
        query["status"] = status
    if min_amount is not None:
        query["amount"] = {"$gte": min_amount}
    if max_amount is not None:
        if "amount" in query:
            query["amount"]["$lte"] = max_amount
        else:
            query["amount"] = {"$lte": max_amount}

    try:
        donations = await Donation.find(query).to_list()
        donation_list = [donation.model_dump() for donation in donations]
        for donation in donation_list:
            donation["id"] = str(donation["id"])
        return donation_list
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while searching donations: {str(e)}",
        )
