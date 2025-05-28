from fastapi import APIRouter, HTTPException, Depends
from app.services.user_service import get_user_by_id
from app.utils.jwt_handler import jwt_required
from app.services.foodbank.volunteer_management_service import (
    get_list_volunteer_in_db,
    update_application_status_in_db,
    get_list_foodbank_application_in_db,
    get_application_detail,
    get_job_detail_in_db,
    add_volunteer_activity_in_db,
)

router = APIRouter()


@router.get("/volunteers/{event_id}")
async def get_list_volunteer_application(
    event_id: str, payload: dict = Depends(jwt_required), status: str | None = None
):
    """
    Allow food bank admin to retrieve the list of volunteer application for specific event
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param event_id: An event ID, the application is stored including the event ID
    """

    # Validate if the request is made from Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can retrieve the list of volunteer application",
        )

    if not status == "approved" and not status == "pending":
        raise HTTPException(
            status_code=400, detail="Status must be either approved or pending!"
        )
    # Retrieve the list of volunteer application
    volunteers = await get_list_volunteer_in_db(event_id=event_id, status=status)

    if len(volunteers) == 0:
        raise HTTPException(
            status_code=404, detail=f"The list of volunteer applications is Empty"
        )

    return {"status": "success", "volunteers": volunteers}


@router.put("/volunteers/{application_id}")
async def update_status_of_application(
    application_id: str,
    payload: dict = Depends(jwt_required),
    application_data: dict = {},
):
    """
    Allow food bank admin to update the status of the specific application
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param application_id: A unique identifier for application in DB
    :return a success message
    """

    # Validate if the request is made from Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can update the status of the specific application!",
        )

    if not application_data["updated_status"]:
        raise HTTPException(
            status_code=400, detail="New status is required and can not be empty!"
        )

    if (
        application_data["updated_status"] != "approved"
        and application_data["updated_status"] != "rejected"
    ):
        raise HTTPException(
            status_code=400, detail="Status must be either approved or rejected!"
        )

    # Update the status of an application in db
    application = await update_application_status_in_db(
        application_id=application_id, updated_status=application_data["updated_status"]
    )

    return {"status": "success", "application": application}


@router.get("/volunteer/{volunteer_id}")
async def get_volunteer_detailed_info(
    volunteer_id: str, payload: dict = Depends(jwt_required)
):
    """
    Allow food bank admin to retrieve the detailed information about specific volunteer
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param status:
    :return a success message and an information of a volunteer
    """
    # Validate if the request is made from Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can retrieve the list of appointments",
        )

    # Get volunteer information from db
    volunteer = await get_user_by_id(id=volunteer_id)

    volunteer_resp = {
        "id": volunteer["id"],
        "name": volunteer["name"],
        "role": volunteer["role"],
        "email": volunteer["email"],
        "description": volunteer["description"],
        "experiences": volunteer["experiences"],
    }
    return {"status": "success", "volunteer": volunteer_resp}


@router.get("/volunteer-applications")
async def get_list_volunteer_applications(
    payload: dict = Depends(jwt_required), status: str | None = None
):
    """
    Allow foodbank admin to retrieve the list of applications for foodbank positions
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param status: to filter the list approved or pending
    return a list of volunteer application for foodbank positions along with the status
    """

    # Validate if the request is made from Foodbank admin
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can get the list of applications for foodbank positions",
        )

    if not status == "approved" and not status == "pending":
        raise HTTPException(
            status_code=400, detail="Status must be either approved or pending!"
        )

    applications = await get_list_foodbank_application_in_db(
        foodbank_id=payload.get("sub"), status=status
    )

    if len(applications) == 0:
        raise HTTPException(status_code=404, detail="List of applications is empty")

    return {"status": "success", "applications": applications}


@router.post("/volunteer-activity/{application_id}")
async def add_volunteer_activity(
    application_id: str, payload: dict = Depends(jwt_required), activity_data: dict = {}
):
    """
    Allow foodbank admin to add the contribution hours for each application
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param activity_data: A dictionary contain activity information
    """
    # Validate if the request is made from Foodbank admin
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can add the contribution hours for volunteer",
        )

    # Validate the job data
    required_key: list = [
        "date_worked",
        "working_hours",
    ]

    # Start validation those keys
    for key in required_key:
        if not activity_data.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    # Retrieve the foodbank name
    foodbank = await get_user_by_id(id=payload.get("sub"))
    if not foodbank:
        raise HTTPException(status_code=404, detail=f"Foodbank not found!")

    # Retrieve category of the application
    application_detail = await get_application_detail(application_id=application_id)
    if not application_detail:
        raise HTTPException(status_code=404, detail="Application not Found!")

    # Retrieve job information
    job_detail = await get_job_detail_in_db(job_id=application_detail["job_id"])
    if not job_detail:
        raise HTTPException(status_code=404, detail="Job not Found!")

    # Add contribution hours for volunteer in db
    activity = await add_volunteer_activity_in_db(
        application_id=application_id,
        date_worked=activity_data["date_worked"],
        foodbank_name=foodbank["name"],
        category=job_detail["category"],
        working_hours=activity_data["working_hours"],
    )

    return {"status": "success", "activity": activity}
