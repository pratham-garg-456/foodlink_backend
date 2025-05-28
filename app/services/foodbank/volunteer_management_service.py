from fastapi import HTTPException
from beanie import PydanticObjectId
from app.models.application import Application, EventApplication
from app.models.user import User
from app.models.job import Job
from app.utils.time_converter import convert_string_time_to_iso
from app.models.volunteer_activity import VolunteerActivity


async def get_list_volunteer_in_db(event_id: str, status: str):
    """
    Retrieve a list of volunteer application for a specific event
    :param event_id: An event ID, the application is stored including the event ID
    """

    application_list = []

    # Validate the event id if it is valid or not
    # try:
    #     event_id = PydanticObjectId(event_id)
    # except Exception as e:
    #     raise HTTPException(status_code=422, detail=f"Invalid event_id: {e}")

    # Retrieve the event stored in db
    # event = await Event.get(event_id)

    # if not event:
    #     raise HTTPException(
    #         status_code=404, detail="Event ID is not valid or not found"
    #     )
    try:
        applications = await EventApplication.find(
            {"status": status, "event_id": event_id}
        ).to_list()

        for application in applications:
            application = application.model_dump()
            application["id"] = str(application["id"])
            application_list.append(application)

        return application_list
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while fetching the list of application in DB: {e}",
        )
        
        
async def update_application_status_in_db(application_id: str, updated_status: str):
    """
    Update the status of a specific application in db
    :param application_id: A unique identifier for volunteer's application
    :param updated_status: A new status of application (approved or rejected)
    """

    application = await Application.get(PydanticObjectId(application_id))
    if application == None:
        application = await EventApplication.get(PydanticObjectId(application_id))
        if application == None:
            raise HTTPException(
                status_code=404,
                detail="There is no application corresponding with the given ID",
            )
    try:

        application.status = updated_status
        await application.save()
        application = application.model_dump()
        application["id"] = str(application["id"])

        return application
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while updating the application in DB: {e}",
        )
        
        
async def get_list_foodbank_application_in_db(foodbank_id: str, status: str):
    """
    Retrieve a list of volunteer application for foodbank position
    :param status: used to filter the list
    :param foodbank_id: A unique identifier for foodbank
    """

    application_list = []
    try:
        applications = await Application.find(
            Application.foodbank_id == foodbank_id, Application.status == status
        ).to_list()

        for application in applications:
            application = application.model_dump()
            application["id"] = str(application["id"])

            # Retrieve volunteer information based on the volunteer ID
            volunteer = await User.get(
                PydanticObjectId(str(application["volunteer_id"]))
            )
            application["volunteer_name"] = volunteer.name

            # Retrieve job informaation
            job = await Job.get(PydanticObjectId(application["job_id"]))
            application["job_name"] = job.title
            application["job_category"] = job.category

            application_list.append(application)

        return application_list
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while fetching the list of application in DB: {e}",
        )
        
async def get_application_detail(application_id: str):
    """
    Retrieve application details
    :param application_id: An id is created from mongodb
    """

    try:
        application = await Application.get(PydanticObjectId(application_id))
        application = application.model_dump()
        application["id"] = str(application["id"])

        return application
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while fetching the detailed of application in DB: {e}",
        )


async def get_job_detail_in_db(job_id: str):
    """
    Retrieve the job details
    :param job_id: An id is created from mongodb
    """

    try:
        job = await Job.get(PydanticObjectId(job_id))
        job = job.model_dump()
        job["id"] = str(job["id"])

        return job
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while fetching the detailed of a job in DB: {e}",
        )


async def add_volunteer_activity_in_db(
    application_id: str,
    date_worked: str,
    foodbank_name: str,
    category: str,
    working_hours: dict,
):
    """
    Add volunteer activity in db
    :param date_worked: the date that volunteer work
    :param foodbank_name: The foodbank name
    :param category: category of the job
    :working_hours: start time and end time
    """

    # Convert str time to datetime
    start = convert_string_time_to_iso(
        date_time=date_worked, time_str=working_hours["start"]
    )

    end = convert_string_time_to_iso(
        date_time=date_worked, time_str=working_hours["end"]
    )

    date_worked = convert_string_time_to_iso(
        date_time=date_worked, time_str=working_hours["start"]
    )

    working_hours["start"] = start
    working_hours["end"] = end
    try:
        activity = VolunteerActivity(
            application_id=application_id,
            date_worked=date_worked,
            foodbank_name=foodbank_name,
            category=category,
            working_hours=working_hours,
        )

        await activity.save()
        activity = activity.model_dump()
        activity["id"] = str(activity["id"])
        return activity
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while creating the volunteer activity in DB: {e}",
        )