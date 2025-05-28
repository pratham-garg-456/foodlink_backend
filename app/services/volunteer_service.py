from app.models.application import Application, EventApplication
from app.models.volunteer_activity import VolunteerActivity
from app.models.job import Job
from app.models.user import User
from beanie import PydanticObjectId
from fastapi import HTTPException
from datetime import datetime, timezone
from app.models.event import Event, EventInventory


async def add_event_application_in_db(volunteer_id: str, event_id: str, job_id: str):
    """
    Add an application to db
    :param event_id: the event ID
    :param volunteer_id: the volunteer ID
    :param job_id: The unique identifier for available jobs
    """
    try:
        new_application = EventApplication(
            volunteer_id=volunteer_id,
            event_id=event_id,
            job_id=job_id,
        )
        await new_application.insert()
        new_application = new_application.model_dump()
        new_application["id"] = str(new_application["id"])
        return new_application

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while creating a new application in db: {e}",
        )


async def add_foodbank_job_application_in_db(
    volunteer_id: str, foodbank_id: str, job_id: str
):
    """
    Add a foodbank job application to db
    :param volunteer_id: The unique identifier for volunteer
    :param foodbank_id: The unique identifier for foodbank
    :param job_id: The unique identifier for available jobs
    """
    try:
        existing_application = await Application.find_one(
            Application.volunteer_id == volunteer_id,
            Application.foodbank_id == foodbank_id,
            Application.job_id == job_id,
        )
        if existing_application:
            return False

        new_application = Application(
            volunteer_id=volunteer_id,
            foodbank_id=foodbank_id,
            job_id=job_id,
        )

        await new_application.insert()
        new_application = new_application.model_dump()
        new_application["id"] = str(new_application["id"])
        return new_application

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while creating a new application in db: {e}",
        )


async def retrieve_volunteer_activity_in_db(volunteer_id):
    """
    Retrieve the list of volunteer activity
    """
    try:
        volunteer_activity_list = []
        applications = await Application.find(
            Application.volunteer_id == volunteer_id
        ).to_list()
        application_ids = [str(app.id) for app in applications]
        if not application_ids:
            return []
        for app_id in application_ids:
            activities = await VolunteerActivity.find(
                VolunteerActivity.application_id == app_id
            ).to_list()

            for activity in activities:
                activity_dict = activity.model_dump() | {"id": str(activity.id)}
                volunteer_activity_list.append(activity_dict)

        return volunteer_activity_list

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while fetching a list of volunteer activity in db: {e}",
        )


async def retrieve_list_jobs_in_db():
    """
    Retrieve the list of available jobs only
    """

    job_list = []

    try:
        jobs = await Job.find().to_list()

        for job in jobs:
            # Automate the process of updating the status of job
            await job.check_and_update_status()

            if job.status == "available":
                job = job.model_dump()
                job["id"] = str(job["id"])
                # Retrieve foodbank information by using the ID
                foodbank = await User.get(PydanticObjectId(job["foodbank_id"]))
                foodbank = foodbank.model_dump()

                # Add the foodbank name to the list
                job["foodbank_name"] = foodbank["name"]
                job_list.append(job)

        return job_list
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while fetching a list of job in db: {e}",
        )


async def retrieve_specific_job_in_db(job_id: str):
    """
    Retrieve the specific job based on the job id
    """
    try:
        job = await Job.find_one(Job.id == PydanticObjectId(job_id))

        if not job:
            return None
        await job.check_and_update_status()

        if job.status != "available":
            return None

        foodbank = await User.find_one(User.id == PydanticObjectId(job.foodbank_id))
        foodbank_name = foodbank.name if foodbank else "Unknown"

        job_dict = job.model_dump()
        job_dict["id"] = str(job.id)
        job_dict["foodbank_name"] = foodbank_name
        return job_dict

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while fetching a specific job in db: {e}",
        )


async def retrieve_applied_job_in_db(volunteer_id: str):
    """
    Retrieve the applied job based on the volunteer id
    """

    application_list = []

    try:
        applications = await Application.find(
            Application.volunteer_id == volunteer_id,
        ).to_list()

        for application in applications:
            application = application.model_dump()
            application["id"] = str(application["id"])

            # Retrieve foodbank information by using the ID
            foodbank = await User.get(PydanticObjectId(application["foodbank_id"]))
            foodbank = foodbank.model_dump()

            # Add the foodbank name to the list
            application["foodbank_name"] = foodbank["name"]
            application_list.append(application)

        return application_list
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while fetching a list of applied job in db: {e}",
        )


async def delete_application(volunteer_id: str, application_id: str):
    """
    Delete the application based on volunteer id and application id
    """
    try:
        application = await Application.find_one(
            Application.id == PydanticObjectId(application_id),
            Application.volunteer_id == volunteer_id,
        )
        if not application:
            return False
        await application.delete()
        return True

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while deleting job in db: {e}",
        )


async def update_metadata_in_db(
    id: str, experiences: str, description: str, image_url: str, phone_number: str
):
    """
    update metadata for volunteer users in db
    :param id: A mongoDB identifier
    :param experiences: A past experiences about volunteer
    :param description: A brief description about volunteer
    :param image_url: Profile Image
    :param phone_number: Volunteer's Phone Number
    """
    try:
        volunteer = await User.get(PydanticObjectId(id))

        if not volunteer:
            raise HTTPException(status_code=404, detail="User not found!")

        if volunteer.role != "volunteer":
            raise HTTPException(status_code=400, detail="User is not a volunteer")

        volunteer.experiences = experiences
        volunteer.description = description
        volunteer.image_url = image_url
        volunteer.phone_number = phone_number
        volunteer.updated_at = datetime.now(timezone.utc)

        await volunteer.save()
        volunteer = volunteer.model_dump()
        volunteer["id"] = str(volunteer["id"])

        return volunteer

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating the metadata for volunteer: {e}",
        )


async def retrieve_list_of_events_in_db():
    """
    Retrieve the detailed information about an ongoing events
    """
    # Initialize the list with empty array
    event_list = []
    try:
        events = await Event.find().to_list()

        for event in events:
            event = event.model_dump()
            event["id"] = str(event["id"])

            # Fetch event inventory
            event_inventory = await EventInventory.find_one(
                EventInventory.event_id == event["id"]
            )
            
            if event_inventory:
                event_inventory = event_inventory.model_dump()
                event_inventory["id"] = str(event_inventory["id"])
            else:
                event_inventory = []
            event["event_inventory"] = event_inventory
            event_list.append(event)

        return event_list
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching the list of events: {e}",
        )
