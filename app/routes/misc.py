from fastapi import APIRouter, HTTPException, UploadFile, File
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from app.models.service import Service
from app.models.contact import Contact
from app.models.user import User
from app.models.donation import Donation

# Configuration
cloudinary.config(
    cloud_name="dsyakhivg",
    api_key="554361879535433",
    api_secret="5MQvSQUhGVXwUZgr3n_N4bUsV7Q",  # Replace with your actual API secret
    secure=True
)

router = APIRouter()


@router.post("/services")
async def add_available_services(service_data: dict = {}):
    """
    Allow food link admin to add available services of the app
    :param service_data: A service information
    :return A created service is stored in the db
    """
    # Required key in the body
    required_keys = ["title", "description"]
    # Validate it
    for key in required_keys:
        if not service_data.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    # Check if the service is defined already
    is_defined = await Service.find_one(Service.title == service_data.get("title"))

    if is_defined:
        raise HTTPException(
            status_code=401, detail=f"{service_data['title']} defined already!"
        )

    # Creating a new service in the db
    try:
        new_service = Service(
            title=service_data["title"], description=service_data["description"]
        )

        await new_service.insert()
        service_dict = new_service.model_dump()
        service_dict["id"] = str(service_dict["id"])
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while creating new service in db: {e}",
        )

    return {"status": "success", "service": service_dict}


@router.get("/services")
async def retrieve_a_list_of_service():
    """
    Allow FoodLink admin to get the list of services in the db
    :return a list of services which can display to the end users
    """
    # Define a list of a service
    service_list = []

    # Fetch the list of services in the db
    try:
        services = await Service.find().to_list()
        for service in services:
            service_dict = service.model_dump()
            service_dict["id"] = str(service_dict["id"])
            service_list.append(service_dict)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"List is empty or {e}")

    return {"status": "success", "services": service_list}


@router.post("/contact")
async def submit_question(contact_data: dict = {}):
    """
    Allow user to submit a question to FoodLink
    :return a new question stored in the db
    """

    # Required key in the body
    required_keys = ["name", "email", "phone", "subject"]
    # Validate it
    for key in required_keys:
        if not contact_data.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    # Creating a new question in the db
    try:
        new_question = Contact(
            name=contact_data["name"],
            email=contact_data["email"],
            phone=contact_data["phone"],
            subject=contact_data["subject"],
            message=contact_data["message"],
        )

        await new_question.insert()
        question_dict = new_question.model_dump()
        question_dict["id"] = str(question_dict["id"])
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while creating a new question in db: {e}",
        )

    return {"status": "success", "question": new_question}

@router.get("/users")
async def retrieve_list_of_users():
    """
    Allow us to get the list of Users in the db
    :return a list of users which can be display to the end users
    """
    # Define a list of a user
    user_list = []

    # Fetch the list of services in the db
    try:
        users = await User.find().to_list()
        for user in users:
            user_dict = user.model_dump()
            user_dict["id"] = str(user_dict["id"])
            user_list.append(user_dict)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"List is empty or {e}")

    return {"status": "success", "users": user_list}

@router.get("/donations")
async def get_donations_for_foodbank():
    """
    API Endpoint: Retrieve all donations for foodbank.
    """
    total_donations = 0
    donations = await Donation.find().to_list()
    for donation in donations:
        total_donations += donation.amount

    return {
        "status": "success",
        "total_donations": total_donations,
    }

@router.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Upload the image to Cloudinary
        upload_result = cloudinary.uploader.upload(file.file, public_id=file.filename)
        secure_url = upload_result["secure_url"]

        # Return the secure URL
        return {"secure_url": secure_url}
    except Exception as e:
        return {"error": str(e)}

@router.get("/optimize/{public_id}")
def optimize_image(public_id: str):
    # Optimize delivery by resizing and applying auto-format and auto-quality
    optimize_url, _ = cloudinary_url(public_id, fetch_format="auto", quality="auto")
    return {"optimize_url": optimize_url}

@router.get("/auto-crop/{public_id}")
def auto_crop_image(public_id: str):
    # Transform the image: auto-crop to square aspect ratio
    auto_crop_url, _ = cloudinary_url(public_id, width=500, height=500, crop="auto", gravity="auto")
    return {"auto_crop_url": auto_crop_url}

