from fastapi import APIRouter, HTTPException, Depends
from app.utils.jwt_handler import jwt_required
from app.services.volunteer_service import (
    add_foodbank_job_application_in_db,
    add_event_application_in_db,
    retrieve_list_jobs_in_db,
    delete_application,
    retrieve_applied_job_in_db,
    retrieve_specific_job_in_db,
    retrieve_volunteer_activity_in_db,
    update_metadata_in_db,
    retrieve_list_of_events_in_db,
)

router = APIRouter()


@router.post("/application/event")
async def apply_available_jobs_for_event(
    payload: dict = Depends(jwt_required), application_data: dict = {}
):
    """
    Allow volunteer to submit the application to specific event for specific food bank
    :param application_data: A application information
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :return A created application is stored in the db
    """
    if payload.get("role") != "volunteer":
        raise HTTPException(
            status_code=401, detail="Only volunteer can apply application"
        )

    required_key = ["event_id", "job_id"]

    # Start validation those keys
    for key in required_key:
        if not application_data.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    # create a application in db
    new_application = await add_event_application_in_db(
        volunteer_id=payload.get("sub"),
        event_id=application_data["event_id"],
        job_id=application_data["job_id"],
    )

    return {"status": "success", "event_application": new_application}


@router.post("/application/foodbank")
async def apply_available_jobs_for_foodbank(
    payload: dict = Depends(jwt_required), application_data: dict = {}
):
    """
    Allow volunteer to submit the application to available positions from different foodbank
    :param application_data: A application information
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :return A created application is stored in the db
    """
    # Validate if the request is made from a volunteer
    if payload.get("role") != "volunteer":
        raise HTTPException(
            status_code=401, detail="Only volunteer can apply application"
        )

    required_key = ["foodbank_id", "job_id"]

    # Start validation those keys
    for key in required_key:
        if not application_data.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    # create a application in db
    new_application = await add_foodbank_job_application_in_db(
        volunteer_id=payload.get("sub"),
        foodbank_id=application_data["foodbank_id"],
        job_id=application_data["job_id"],
    )
    if new_application == False:
        raise HTTPException(
            status_code=409, detail="You have already applied for this job."
        )

    return {"status": "success", "foodbank_application": new_application}


@router.get("/jobs")
async def retrieve_available_job(payload: dict = Depends(jwt_required)):
    """
    Retrieve the list of available job from different foodbank
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :return a list of available jobs from different foodbank
    """

    # Validate if the request is made from Volunteer
    if payload.get("role") != "volunteer":
        raise HTTPException(
            status_code=401, detail="Only Volunteer get the list of the jobs"
        )

    jobs = await retrieve_list_jobs_in_db()

    if len(jobs) == 0:
        raise HTTPException(status_code=404, detail="There are no posted jobs!")

    return {"status": "success", "jobs": jobs}


@router.get("/activity")
async def retrieve_volunteer_activity(payload: dict = Depends(jwt_required)):
    """
    Retrieve the past activity of the volunteer
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :return the past activity
    """
    if payload.get("role") != "volunteer":
        raise HTTPException(
            status_code=401, detail="Only Volunteer get the list of the jobs"
        )
    volunteer_id = payload.get("sub")
    activity_list = await retrieve_volunteer_activity_in_db(volunteer_id)
    return {"status": "success", "activity_list": activity_list}


@router.get("/job/{job_id}")
async def retrieve_specific_job(job_id: str, payload: dict = Depends(jwt_required)):
    """
    Retrieve the information of the job based on the job id
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param job_id: job id for fetch the job.
    :return the specific job
    """

    # Validate if the request is made from Volunteer
    if payload.get("role") != "volunteer":
        raise HTTPException(
            status_code=401, detail="Only Volunteer get the list of the jobs"
        )
    job = await retrieve_specific_job_in_db(job_id)
    if job is None:
        raise HTTPException(
            status_code=404, detail="Job not found or is no longer available"
        )

    return {"status": "success", "job": job}


@router.get("/applied_job")
async def retrieve_applied_job(payload: dict = Depends(jwt_required)):
    """
    Retrieve the volunteer applied job based on volunteer id
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :return the list of applied jobs
    """
    # Validate if the request is made from Volunteer
    if payload.get("role") != "volunteer":
        raise HTTPException(
            status_code=401, detail="Only Volunteer get the list of the jobs"
        )

    applied_job = await retrieve_applied_job_in_db(volunteer_id=payload.get("sub"))

    if len(applied_job) == 0:
        raise HTTPException(status_code=404, detail="There is no applied jobs!")
    return {"status": "success", "application": applied_job}


@router.delete("/cancel_application/{application_id}")
async def delete_applied_job(
    application_id: str, payload: dict = Depends(jwt_required)
):
    """
    Update the status application to cancel
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param application_id: application id to delete
    :return the list of applied jobs
    """
    # Validate if the request is made from Volunteer
    if payload.get("role") != "volunteer":
        raise HTTPException(
            status_code=401, detail="Only Volunteer get the list of the jobs"
        )

    volunteer_id = payload.get("sub")
    deleted = await delete_application(
        volunteer_id=volunteer_id, application_id=application_id
    )
    if deleted == False:
        raise HTTPException(
            status_code=404, detail="Application not found or does not belong to you."
        )
    else:
        return {"status": "success", "message": "Application has been canceled."}


@router.put("/metadata")
async def create_volunteer_metadata(
    payload: dict = Depends(jwt_required), volunteer_data: dict = {}
):
    """
    Allow volunteer to add more informations about them such as past experiences and descrition
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param volunteer_data: Information of volunteer
    """
    # Validate if the request is made from Volunteer
    if payload.get("role") != "volunteer":
        raise HTTPException(
            status_code=401, detail="Only Volunteer can update their information"
        )

    # Update the metadata for volunteer in db
    volunteer = await update_metadata_in_db(
        id=payload.get("sub"),
        experiences=volunteer_data["experiences"],
        description=volunteer_data["description"],
        image_url=volunteer_data["image_url"],
        phone_number=volunteer_data["phone_number"],
    )

    return {"status": "success", "volunteer": volunteer}


@router.get("/events")
async def retrieve_list_of_ongoing_events(payload: dict = Depends(jwt_required)):
    """
    Allow volunteer to get the list of ongoing foodbank events
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    """

    # Validate if the request is made from volunteer
    if payload.get("role") != "volunteer":
        raise HTTPException(
            status_code=401, detail="Only volunteer can retrieve the list of events"
        )

    events = await retrieve_list_of_events_in_db()

    return {"status": "success", "events": events}
