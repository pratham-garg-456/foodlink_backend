from fastapi import APIRouter, HTTPException, Depends
from app.utils.jwt_handler import jwt_required
from app.services.foodbank.appointment_service import (
    get_list_appointments_in_db,
    update_appointment_status_in_db,
    reschedule_appointment_in_db,
    get_appointments_by_foodbank,
)

router = APIRouter()


@router.get("/appointments")
async def fetch_appointments_by_foodbank(payload: dict = Depends(jwt_required)):
    """
    API route to get all appointments for a specific food bank.
    Only Food Bank Admins can access this route.
    """
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401, detail="Only FoodBank admins can access this route."
        )

    appointments = await get_appointments_by_foodbank(payload.get("sub"))
    return {"status": "success", "appointments": appointments}


@router.get("/appointments")
async def get_list_of_appointments(
    payload: dict = Depends(jwt_required), status: str | None = None
):
    """
    Allow food bank admin to retrieve the list of appointments
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :param status: Pending, confirmed, or rescheduled, or cancelled
    :return a success message and a list of appointments
    """

    # Validate if the request is made from Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can retrieve the list of appointments",
        )

    if (
        not status == "picked"
        and not status == "scheduled"
        and not status == "cancelled"
        and not status == "rescheduled"
    ):
        raise HTTPException(
            status_code=400,
            detail="Status of an appointment must be confirmed or pending or cancelled or rescheduled",
        )

    appointments = await get_list_appointments_in_db(
        foodbank_id=payload.get("sub"), status=status
    )

    if len(appointments) == 0:
        raise HTTPException(
            status_code=404, detail="There are no upcoming appointments!"
        )

    return {"status": "success", "appointments": appointments}


@router.put("/appointment/{appointment_id}")
async def update_status_of_appointment(
    appointment_id: str,
    payload: dict = Depends(jwt_required),
    appointment_data: dict = {},
):
    """
    Allow food bank admin to confirm, reschedule, or cancel the appointment,
    :param appointment_id: An ID for appointment in db
    :param appointment_data: An updated_status for the specific appointments
    """

    # Validate if the request is made from Foodbank user
    if payload.get("role") != "foodbank":
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin can update the status of the appointment",
        )

    if not appointment_data["updated_status"]:
        raise HTTPException(
            status_code=400, detail="New status is required and can not be empty!"
        )

    if (
        appointment_data["updated_status"] != "picked"
        and appointment_data["updated_status"] != "cancelled"
    ):
        raise HTTPException(
            status_code=400,
            detail="Status must be picked or cancelled!",
        )

    # Update the appointment in db
    appointment = await update_appointment_status_in_db(
        appointment_id=appointment_id, updated_status=appointment_data["updated_status"]
    )

    return {"status": "success", "appointment": appointment}


@router.put("/appointment/{appointment_id}/reschedule")
async def reschedule_appointment(
    appointment_id: str,
    reschedule_data: dict,
    payload: dict = Depends(jwt_required),
):
    """
    Allows the food bank admin or individual to reschedule an appointment.
    """

    # Validate if the request is made from Foodbank user or Individual
    if payload.get("role") not in ["foodbank", "individual"]:
        raise HTTPException(
            status_code=401,
            detail="Only FoodBank admin or Individuals can reschedule an appointment",
        )

    # Call the database function
    appointment = await reschedule_appointment_in_db(
        appointment_id=appointment_id, reschedule_data=reschedule_data
    )

    return {
        "status": "success",
        "message": "Appointment rescheduled successfully",
        "appointment": appointment,
    }
