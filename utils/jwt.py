import os
from datetime import datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from utils.db import is_token_blacklisted, valid_email_from_db
from utils.error import print_error, CREDENTIALS_EXCEPTION

load_dotenv()

REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days


# Helper to read numbers using var envs
def cast_to_number(id):
    temp = os.environ.get(id)
    if temp is not None:
        try:
            return float(temp)
        except ValueError:
            return None
    return None


# Configuration
API_SECRET_KEY = os.environ.get("API_SECRET_KEY") or None
if API_SECRET_KEY is None:
    raise BaseException("Missing API_SECRET_KEY env var.")
API_ALGORITHM = os.environ.get("API_ALGORITHM") or "HS256"
API_ACCESS_TOKEN_EXPIRE_MINUTES = (
    cast_to_number("API_ACCESS_TOKEN_EXPIRE_MINUTES") or 60
)

# Token url (We should later create a token url that accepts just a user and a password to use it with Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# Create token internal function
def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, API_SECRET_KEY, algorithm=API_ALGORITHM)
    return encoded_jwt


# Create token for an email
def create_token(email):
    access_token_expires = timedelta(minutes=API_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    return access_token


async def get_current_user_email(request):
    token: str = await get_current_user_token(request)

    if is_token_blacklisted(request, token) is not None:
        print_error("Token is blacklisted")
        raise CREDENTIALS_EXCEPTION

    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            print_error("Email is None")
            raise CREDENTIALS_EXCEPTION
    except jwt.PyJWTError as e:
        print_error("Invalid token", e)
        raise CREDENTIALS_EXCEPTION

    if valid_email_from_db(request, email):
        return email

    print_error("get_current_user_email", "Something went wrong")
    raise CREDENTIALS_EXCEPTION


async def get_current_user_token(request):
    token: str = await oauth2_scheme(request)
    return token


def create_refresh_token(email):
    expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    return create_access_token(data={"sub": email}, expires_delta=expires)


def decode_token(token):
    return jwt.decode(token, API_SECRET_KEY, algorithms=[API_ALGORITHM])
