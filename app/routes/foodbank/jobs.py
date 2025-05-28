from fastapi import APIRouter, HTTPException, Depends
from app.services.user_service import get_user_by_id
from app.utils.jwt_handler import jwt_required
from app.services.foodbank.job_service import (
    add_a_new_job_in_db,
    add_a_new_event_job_in_db,
    list_foodbank_job_in_db,
    list_event_job_in_db,
    update_existing_job_info_in_db,
)

from app.models.event import Event
from beanie import PydanticObjectId

router = APIRouter()


@router.post("/job")
async def post_a_new_job(payload: dict = Depends(jwt_required), job_data: dict = {}):
    """
    Allow foodbank admin to create a new job within foodbank for the volunteer
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param job_data: A dictionary contains job information
    """

    # Validate if the request is made from Foodbank admin
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401, detail="Only FoodBank admin can post a new job"
        )

    # Validate the job data
    required_key: list = [
        "title",
        "description",
        "location",
        "category",
        "deadline",
        "status",
    ]

    # Start validation those keys
    for key in required_key:
        if not job_data.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    # Validate if the foodbank ID is a valid registered foodbank
    foodbank = await get_user_by_id(id=payload.get("sub"))

    if not foodbank:
        raise HTTPException(status_code=404, detail=f"Foodbank Not Found!")

    # Validate the given status if it is available or unavailable
    if job_data["status"] != "available" and job_data["status"] != "unavailable":
        raise HTTPException(
            status_code=400,
            detail="Status of a job must be either available or unavailable!",
        )

    # Add a new job in db
    job = await add_a_new_job_in_db(foodbank_id=payload.get("sub"), job_data=job_data)

    return {"status": "success", "job": job}


@router.post("/event-job")
async def post_a_new_event_job(
    payload: dict = Depends(jwt_required), job_data: dict = {}
):
    """
    Allow foodbank admin to create a new job for specific event
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param job_data: A dictionary contains job information
    """

    # Validate if the request is made from Foodbank admin
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401, detail="Only FoodBank admin can post a new job"
        )

    # Validate the job data
    required_key: list = [
        "event_id",
        "title",
        "description",
        "location",
        "category",
        "deadline",
        "status",
    ]

    # Start validation those keys
    for key in required_key:
        if not job_data.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    # Validate if the foodbank ID is a valid registered foodbank
    foodbank = await get_user_by_id(id=payload.get("sub"))

    if not foodbank:
        raise HTTPException(status_code=404, detail=f"Foodbank Not Found!")

    # Validate if the event ID is a valid event
    event = await Event.get(PydanticObjectId(job_data["event_id"]))

    if not event:
        raise HTTPException(status_code=404, detail="Event not found!")

    # Validate the given status if it is available or unavailable
    if job_data["status"] != "available" and job_data["status"] != "unavailable":
        raise HTTPException(
            status_code=400,
            detail="Status of a job must be either available or unavailable!",
        )

    # Add a new job in db
    job = await add_a_new_event_job_in_db(
        foodbank_id=payload.get("sub"), job_data=job_data
    )

    return {"status": "success", "job": job}


@router.get("/jobs")
async def get_list_of_jobs(payload: dict = Depends(jwt_required)):
    """
    Allow foodbank admin to retrieve the list of jobs
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    """

    # Validate if the request is made from Foodbank admin
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401, detail="Only FoodBank admin can get the list of jobs"
        )

    jobs = await list_foodbank_job_in_db()

    return {"status": "success", "jobs": jobs}


@router.get("/event-jobs")
async def get_list_of_jobs(payload: dict = Depends(jwt_required)):
    """
    Allow foodbank admin to retrieve the list of jobs
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    """

    # Validate if the request is made from Foodbank admin
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401, detail="Only FoodBank admin can get the list of jobs"
        )

    jobs = await list_event_job_in_db()

    return {"status": "success", "jobs": jobs}


@router.put("/job/{job_id}")
async def update_job_information(
    job_id: str | None, payload: dict = Depends(jwt_required), job_data: dict = {}
):
    """
    Allow foodbank admin to update the existing job information.
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param job_id: Used to identify the specific job
    """

    # Validate if the request is made from Foodbank admin
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401, detail="Only FoodBank admin can update the existing job"
        )

    # Validate the job data
    required_key: list = [
        "title",
        "description",
        "location",
        "category",
        "deadline",
        "status",
    ]

    # Start validation those keys
    for key in required_key:
        if not job_data.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    # Validate if the foodbank ID is a valid registered foodbank
    foodbank = await get_user_by_id(id=payload.get("sub"))

    if not foodbank:
        raise HTTPException(status_code=404, detail=f"Foodbank Not Found!")

    # Validate the given status if it is available or unavailable
    if job_data["status"] != "available" and job_data["status"] != "unavailable":
        raise HTTPException(
            status_code=400,
            detail="Status of a job must be either available or unavailable!",
        )

    updated_job = await update_existing_job_info_in_db(job_id=job_id, job_data=job_data)
    
    return {"status": "success", "job": updated_job}