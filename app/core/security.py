from datetime import datetime
from datetime import timedelta

from jose import jwt
from jose import JWTError

from passlib.context import CryptContext

from app.core.config import settings
from datetime import timedelta
from datetime import datetime
import uuid
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

pwd_context = CryptContext(
    # schemes=["bcrypt"],
    schemes=["argon2"],
    deprecated="auto"
)


def hash_password(password: str):
    print("=" * 50)
    print(f"Password Length: {len(password)}")
    print("=" * 50)

    return pwd_context.hash(password)


def verify_password(
        plain_password: str,
        hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# def create_access_token(data: dict):

#     expire = datetime.utcnow() + timedelta(
#         minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
#     )

#     payload = data.copy()

#     payload.update(
#         {
#             "exp": expire
#         }
#     )

#     return jwt.encode(
#         payload,
#         settings.SECRET_KEY,
#         algorithm=settings.ALGORITHM
#     )

# def create_access_token(data: dict):

#     payload = data.copy()

#     expire = datetime.utcnow() + timedelta(
#         minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
#     )

#     payload.update(
#         {
#             "exp": expire,
#             "token_type": "access"
#         }
#     )

#     return jwt.encode(
#         payload,
#         settings.SECRET_KEY,
#         algorithm=settings.ALGORITHM
#     )

def create_access_token(data: dict):

    payload = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update(
        {
            "exp": expire,
            "token_type": "access",
            "jti": str(uuid.uuid4())
        }
    )

    print("=" * 50)
    print("Creating Access Token")
    print(f"User: {payload.get('sub')}")
    print(f"Role: {payload.get('role')}")
    print(f"JTI: {payload.get('jti')}")
    print("=" * 50)

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

# def create_refresh_token(data: dict):

#     payload = data.copy()

#     expire = datetime.utcnow() + timedelta(
#         days=settings.REFRESH_TOKEN_EXPIRE_DAYS
#     )

#     payload.update(
#         {
#             "exp": expire,
#             "token_type": "refresh"
#         }
#     )

#     return jwt.encode(
#         payload,
#         settings.SECRET_KEY,
#         algorithm=settings.ALGORITHM
#     )


def create_refresh_token(data: dict):

    payload = data.copy()

    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload.update(
        {
            "exp": expire,
            "token_type": "refresh",
            "jti": str(uuid.uuid4())
        }
    )

    print("=" * 50)
    print("Creating Refresh Token")
    print(f"User: {payload.get('sub')}")
    print(f"Role: {payload.get('role')}")
    print(f"JTI: {payload.get('jti')}")
    print("=" * 50)

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def decode_token(token: str):

    try:

        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

    except JWTError:

        return None

def get_current_user(
        token: str = Depends(oauth2_scheme)
):

    payload = decode_token(token)

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return payload