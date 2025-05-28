from app.models.appointment import Appointment
from fastapi import HTTPException
from beanie import PydanticObjectId
from datetime import datetime, timezone


async def get_list_appointments_in_db(foodbank_id: str, status: str):
    """
    Retrieve a list of appointments
    :param foodbank_id: A unique identifier for foodbank is used for filtering out the appointments
    """

    appointment_list = []

    appointments = await Appointment.find(
        Appointment.foodbank_id == foodbank_id, Appointment.status == status
    ).to_list()

    try:
        for appointment in appointments:
            appointment = appointment.model_dump()
            appointment["id"] = str(appointment["id"])
            appointment_list.append(appointment)

        return appointment_list
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while fetching the list of appointments: {e}",
        )


async def update_appointment_status_in_db(appointment_id: str, updated_status: str):
    """
    Update the status of a specific appointment in db
    :param appointment_id: A unique identifier for volunteer's appointment
    :param updated_status: A new status of appointment (approved or rejected)
    """

    appointment = await Appointment.get(PydanticObjectId(appointment_id))

    try:
        appointment.status = updated_status
        await appointment.save()
        appointment = appointment.model_dump()
        appointment["id"] = str(appointment["id"])

        return appointment
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while updating the appointment in DB: {e}",
        )


async def reschedule_appointment_in_db(appointment_id: str, reschedule_data: dict):
    """
    Reschedules an appointment to a new date and time.

    :param appointment_id: The ID of the appointment to reschedule.
    :param reschedule_data: A dictionary containing the new start and end time.
    :return: The updated appointment details.
    """
    try:
        # Fetch the appointment from the database
        appointment = await Appointment.get(PydanticObjectId(appointment_id))

        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found.")

        # Extract new start and end times
        new_start_time = reschedule_data.get("start_time")
        new_end_time = reschedule_data.get("end_time")

        if not new_start_time or not new_end_time:
            raise HTTPException(
                status_code=400, detail="New start and end time must be provided."
            )

        # Convert to datetime objects
        new_start_time = datetime.fromisoformat(new_start_time)
        new_end_time = datetime.fromisoformat(new_end_time)

        if new_start_time >= new_end_time:
            raise HTTPException(
                status_code=400, detail="End time must be after start time."
            )

        # ✅ Optional: Check if the new time slot is available
        is_available = await check_time_slot_availability(
            appointment.foodbank_id, new_start_time, new_end_time
        )
        if not is_available:
            raise HTTPException(
                status_code=400, detail="New time slot is not available."
            )

        # Update appointment details
        appointment.start_time = new_start_time
        appointment.end_time = new_end_time
        appointment.status = "rescheduled"
        appointment.last_updated = datetime.now(timezone.utc)

        # Save the updated appointment
        await appointment.save()

        # Convert the updated appointment to a dictionary for response
        updated_appointment = appointment.model_dump()
        updated_appointment["id"] = str(updated_appointment["id"])

        return updated_appointment

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred while rescheduling: {str(e)}"
        )


async def get_appointments_by_foodbank(foodbank_id: str):
    """
    Fetch all appointments for a specific food bank.

    :param foodbank_id: The ID of the food bank.
    :return: A list of appointment objects.
    """
    try:
        appointments = await Appointment.find(
            Appointment.foodbank_id == foodbank_id
        ).to_list()

        # Convert ObjectId to string for JSON response
        for appointment in appointments:
            appointment = appointment.model_dump()
            appointment["id"] = str(appointment["id"])

        return appointments

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching appointments: {str(e)}",
        )


async def check_time_slot_availability(
    foodbank_id: str, start_time: datetime, end_time: datetime
) -> bool:
    """
    Checks if the new appointment time slot is available.

    :param foodbank_id: The ID of the food bank.
    :param start_time: The new proposed start time.
    :param end_time: The new proposed end time.
    :return: True if the time slot is available, False otherwise.
    """
    overlapping_appointments = await Appointment.find(
        {
            "foodbank_id": foodbank_id,
            "start_time": {
                "$lt": end_time
            },  # Appointments that start before the new end time
            "end_time": {
                "$gt": start_time
            },  # Appointments that end after the new start time
        }
    ).to_list()

    return (
        len(overlapping_appointments) == 0
    )  # If no overlapping appointments, the slot is available
