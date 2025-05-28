import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Header
from app.config import settings
from passlib.context import CryptContext


SECRET_KEY = settings.SECRET_KEY  # Store securely in .env
ALGORITHM = "HS256"

# Password hasing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_backend_token(id: str, role: str, expires_in: int = 3600):
    """
    Generate a JWT token.
    :param id: The MongoDB ID
    :param role: The user's role (individual, donor, volunteer, foodbank).
    :param expires_in: Token validity period in seconds (default: 1 hour).
    :return: Encoded JWT token.
    """
    issued_time = datetime.now(timezone.utc)
    expiration = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    payload = {
        "sub": id,
        "role": role,
        "exp": expiration,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    res = {"token": token, "iat": issued_time, "exp": expiration}

    return res

def validate_backend_token(token: str):
    """
    Validate the JWT token.
    :param token: The JWT token from the Authorization header.
    :return: Decoded payload if valid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Contains claims like sub, role, business_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")



def jwt_required(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token missing or invalid")

    token = authorization.split(" ")[1]
    return validate_backend_token(token)