from fastapi import APIRouter, HTTPException, Depends
from app.services.user_service import (
    get_user_by_email_from_db,
    create_user_in_db,
    get_user_by_id,
)
from app.utils.jwt_handler import (
    get_password_hash,
    verify_password,
    create_backend_token,
    jwt_required,
)

router = APIRouter()


@router.post("/register")
async def signup(user_data: dict = {}):
    """
    Allow users to sign up their account to FoodLink
    :param user_data: A user information contains name, role, email, and password
    :return A successful message indicates that the user is stored in the db
    """

    # Define a required body
    required_keys = ["name", "role", "email", "password", "confirm_password"]
    # Validate each key in the body
    for key in required_keys:
        if not user_data.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    if not user_data["confirm_password"] == user_data["password"]:
        raise HTTPException(status_code=401, detail="Password does not match!")

    # Validate the email as an username for user:
    user = await get_user_by_email_from_db(email=user_data["email"])

    if user:
        raise HTTPException(
            status_code=400, detail=f"{user_data['email']} already registered"
        )

    # Hash the input password
    try:
        hashed_password = get_password_hash(user_data["password"])
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"An error occurred while hashing the password: {e}"
        )

    # Store the new user into a db
    new_user = await create_user_in_db(
        name=user_data["name"],
        role=user_data["role"],
        email=user_data["email"],
        password=hashed_password,
    )

    return {"status": "success", "user": new_user}


@router.post("/signin")
async def signin(user_data: dict = {}):
    """
    Allow users to signin to FoodLink
    :param user_data: A user information contains email and plain password
    :return A successful message indicates that user is authenticated
    """
    # Define a required body
    required_keys = ["email", "password"]
    # Validate each key in the body
    for key in required_keys:
        if not user_data.get(key):
            raise HTTPException(
                status_code=400, detail=f"{key} is required and cannot be empty"
            )

    # Fetch the stored user in the db
    user = await get_user_by_email_from_db(email=user_data["email"])

    # Compare the input password with the hashed password stored in the db
    if not user or not verify_password(user_data["password"], user["password"]):
        raise HTTPException(status_code=401, detail=f"Invalid email or password")

    # Generate Backend Token
    backend_token = create_backend_token(id=user["id"], role=user["role"])

    return {
        "status": "success",
        "id": user["id"],
        "role": user["role"],
        "token": backend_token["token"],
        "issued_at": backend_token["iat"],
        "expires_in": backend_token["exp"],
    }


@router.get("/profile")
async def get_your_profile(payload: dict = Depends(jwt_required)):
    """
    Validate the given token
    :param payload: Decoded JWT containing user claims (validated via jwt_required).
    :return success message and information of user which is extracted from token
    """

    # Get user id from payload
    user_id = payload.get("sub")

    # Retrieve user information from DB
    user = await get_user_by_id(id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found!")

    return {"status": "success", "user": user}

@router.get("signout")
async def signout():
    """
    Allow users to sign out from the application
    """
    return {"status": "success", "message": "You have successfully signed out"}