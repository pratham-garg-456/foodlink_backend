from fastapi import APIRouter, HTTPException, Depends, Query
from app.utils.jwt_handler import jwt_required
from app.services.foodbank.donation_service import (
    search_donations,
    get_all_donations,
)
from typing import Optional
from datetime import datetime

router = APIRouter()


@router.get("/donations")
async def get_donations_for_foodbank(payload: dict = Depends(jwt_required)):
    """
    API Endpoint: Retrieve all donations for foodbank.
    """

    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401, detail="Only food banks can retrieve list of donations"
        )

    donations = await get_all_donations(foodbank_id=payload.get("sub"))

    return {
        "status": "success",
        "donations": donations,
    }


@router.get("/donations/search")
async def search_for_donations(
    donor_id: Optional[str] = None,
    donation_id: Optional[str] = None,
    start_time: Optional[datetime] = Query(
        None, description="Start time in ISO format"
    ),
    end_time: Optional[datetime] = Query(None, description="End time in ISO format"),
    status: Optional[str] = None,
    min_amount: Optional[float] = Query(None, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, description="Maximum amount"),
    payload: dict = Depends(jwt_required),
):
    """
    Search donations based on various criteria.
    """
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=403, detail="Only foodbanks can search donations"
        )

    donations = await search_donations(
        foodbank_id=payload.get("sub"),
        donor_id=donor_id,
        donation_id=donation_id,
        start_time=start_time,
        end_time=end_time,
        status=status,
        min_amount=min_amount,
        max_amount=max_amount,
    )

    return {"status": "success", "donations": donations}
