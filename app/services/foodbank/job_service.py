from app.models.job import Job, EventJob
from datetime import datetime
from app.utils.time_converter import convert_string_time_to_iso
from fastapi import HTTPException
from beanie import PydanticObjectId


async def add_a_new_job_in_db(foodbank_id: str, job_data: dict):
    """
    Create a new job in DB
    :param job_data : A dictionary contains job information
    """

    # Convert the deadline time str to UTC ISO format
    job_data["deadline"] = convert_string_time_to_iso(
        job_data["deadline"].split(" ")[0], job_data["deadline"].split(" ")[1]
    )

    try:
        job = Job(
            foodbank_id=foodbank_id,
            title=job_data["title"],
            description=job_data["description"],
            location=job_data["location"],
            category=job_data["category"],
            deadline=job_data["deadline"],
            status=job_data["status"],
        )

        await job.insert()
        job = job.model_dump()
        job["id"] = str(job["id"])
        return job
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating a new job in db: {e}",
        )


async def add_a_new_event_job_in_db(foodbank_id: str, job_data: dict):
    """
    Create a new event job in DB
    :param job_data : A dictionary contains job information
    """

    # Convert the deadline time str to UTC ISO format
    job_data["deadline"] = convert_string_time_to_iso(
        job_data["deadline"].split(" ")[0], job_data["deadline"].split(" ")[1]
    )

    try:
        event_job = EventJob(
            event_id=job_data["event_id"],
            foodbank_id=foodbank_id,
            title=job_data["title"],
            description=job_data["description"],
            location=job_data["location"],
            category=job_data["category"],
            deadline=job_data["deadline"],
            status=job_data["status"],
        )

        await event_job.insert()
        event_job = event_job.model_dump()
        event_job["id"] = str(event_job["id"])
        return event_job
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating a new event job in db: {e}",
        )


async def list_foodbank_job_in_db():
    """
    Retrieve the list of jobs within the foodbank
    """

    job_list = []

    try:
        jobs = await Job.find().to_list()

        for job in jobs:
            # Automate process updating the job status post
            await job.check_and_update_status()
            job = job.model_dump()
            job["id"] = str(job["id"])
            job_list.append(job)
        return job_list
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching the list of job in db: {e}",
        )


async def list_event_job_in_db():
    """
    Retrieve the list of jobs within the specific events
    """

    job_list = []

    try:
        jobs = await Job.find(Job.category == "Event").to_list()

        for job in jobs:
            # Automate process updating the job status post
            await job.check_and_update_status()
            job = job.model_dump()
            job["id"] = str(job["id"])
            job_list.append(job)
        return job_list
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching the list of job in db: {e}",
        )


async def update_existing_job_info_in_db(job_id: str, job_data: dict):
    """
    Update the existing job information
    :param job_id: Used to identify the job that we are looking for
    :param job_data: Job new information
    """

    job = await Job.get(PydanticObjectId(job_id))

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Convert deadline string time to ISO format
    deadline = convert_string_time_to_iso(
        job_data["deadline"].split(" ")[0], job_data["deadline"].split(" ")[1]
    )

    job_data["deadline"] = datetime.fromisoformat(deadline)

    try:
        for key, value in job_data.items():
            setattr(job, key, value)

        await job.save()
        job = job.model_dump()
        job["id"] = str(job["id"])
        return job
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while updating the job in db: {e}",
        )
