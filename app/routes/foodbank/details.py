from fastapi import APIRouter, HTTPException, Depends
from app.utils.jwt_handler import jwt_required
from app.services.foodbank.details_service import update_details_information

router = APIRouter()


@router.put("/metadata")
async def update_foodbank_information(
    payload: dict = Depends(jwt_required), foodbank_data: dict = {}
):
    """
    Allow foodbank admin to add/update their informations about them such as description, location, operating hours, and services they offer
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param foodbank_data : Information of foodbank
    """

    # Validate if the request is made from Foodbank
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401, detail="Only Foodbank can update their information"
        )

    foodbank = await update_details_information(
        id=payload.get("sub"),
        desc=foodbank_data["description"],
        location=foodbank_data["location"],
        operating_hours=foodbank_data["operating_hours"],
        services=foodbank_data["services"],
        phone_number=foodbank_data["phone_number"],
        image_url=foodbank_data["image_url"],
    )

    return {"status": "success", "foodbank": foodbank}
