from fastapi import APIRouter, HTTPException, Depends
from app.services.donor_service import (
    create_donation_in_db,
    get_donations_by_user,
    update_donor_detailed_info_in_db,
    retrieve_list_of_events_in_db,
)

from app.utils.jwt_handler import jwt_required

router = APIRouter()


@router.post("/donations")
async def create_donation(
    payload: dict = Depends(jwt_required), donation_data: dict = {}
):
    """
    API Endpoint: Allow only donors to make a monetary donation.
    """
    if payload.get("role") != "donor":
        raise HTTPException(status_code=401, detail="Only donors can make donations")

    required_key = ["amount", "foodbank_id"]

    # Validate required keys
    for key in required_key:
        if not donation_data.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    if donation_data["amount"] <= 0:
        raise HTTPException(
            status_code=400, detail="Donation amount must be greater than zero"
        )

    # Create the donation record
    donation = await create_donation_in_db(
        donor_id=payload.get("sub"), donation_data=donation_data
    )

    return {
        "status": "success",
        "message": "Donation recorded successfully",
        "donation": donation,
    }


@router.get("/donations")
async def get_donations_for_donor(payload: dict = Depends(jwt_required)):
    """
    API Endpoint: Retrieve all donations made by the donor.
    """
    if payload.get("role") != "donor":
        raise HTTPException(
            status_code=401, detail="Only donors can retrieve donation details"
        )

    donations = await get_donations_by_user(donor_id=payload.get("sub"))
    return {"status": "success", "donations": donations}


@router.put("/metadata")
async def update_donor_metadata(
    payload: dict = Depends(jwt_required), donor_data: dict = {}
):
    """
    Allow donor to add more informations about them such as image url, description, phone number
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param donor_data: Information of donor
    """
    # Validate if the request is made from donor
    if payload.get("role") != "donor":
        raise HTTPException(
            status_code=401, detail="Only donor can update their information"
        )

    # Update the metadata for donor in db
    donor = await update_donor_detailed_info_in_db(
        id=payload.get("sub"),
        desc=donor_data["description"],
        image_url=donor_data["image_url"],
        phone_number=donor_data["phone_number"],
    )

    return {"status": "success", "donor": donor}


@router.get("/events")
async def retrieve_list_of_ongoing_events(payload: dict = Depends(jwt_required)):
    """
    Allow donor to get the list of ongoing foodbank events
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    """

    # Validate if the request is made from donor
    if payload.get("role") != "donor":
        raise HTTPException(
            status_code=401, detail="Only donor can retrieve the list of events"
        )

    events = await retrieve_list_of_events_in_db()

    return {"status": "success", "events": events}
