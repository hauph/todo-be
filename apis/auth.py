from datetime import datetime
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
from authlib.integrations.starlette_client import OAuthError, OAuth
from starlette.config import Config
from utils.db import (
    get_db,
    valid_email_from_db,
)
from utils.jwt import (
    create_token,
    create_refresh_token,
    decode_token,
)
from utils.error import print_error, CREDENTIALS_EXCEPTION
from utils.env_loader import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    SECRET_KEY,
    FRONTEND_URL,
)
from utils.ses import verify_email
from controllers.user import create_user, get_user_by_email


# OAuth settings
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException(
        "Missing env variables GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET"
    )

# Set up oauth
config_data = {
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Create the auth app
auth_app = FastAPI()

# Set up the middleware to read the request session
if SECRET_KEY is None:
    raise BaseException("Missing SECRET_KEY")
auth_app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Frontend URL:
FRONTEND_URL = FRONTEND_URL or "http://127.0.0.1:8000/token"


@auth_app.route("/login")
async def login(request: Request):
    redirect_uri = FRONTEND_URL  # This creates the url for our /auth endpoint
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_app.route("/token")
async def auth(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        print_error("OAuthError", error)
        raise CREDENTIALS_EXCEPTION

    try:
        user = access_token["userinfo"]
        email = access_token["userinfo"]["email"]
        verify_email(email)
        db = get_db(request)
        db_user = get_user_by_email(db, email)
        if db_user is None:
            create_user(db=db, user=user)

        return JSONResponse(
            {
                "result": True,
                "access_token": create_token(email),
                "refresh_token": create_refresh_token(email),
            }
        )
    except Exception as e:
        print_error("Try token", e)
        raise CREDENTIALS_EXCEPTION


@auth_app.post("/refresh")
async def refresh(request: Request):
    try:
        # Only accept post requests
        if request.method == "POST":
            form = await request.json()
            if form.get("grant_type") == "refresh_token":
                token = form.get("refresh_token")
                payload = decode_token(token)
                # Check if token is not expired
                if datetime.utcfromtimestamp(payload.get("exp")) > datetime.utcnow():
                    email = payload.get("sub")
                    try:
                        db_user = valid_email_from_db(request, email)
                        if db_user:
                            # Create and return token
                            return JSONResponse(
                                {"result": True, "access_token": create_token(email)}
                            )
                    except Exception as e:
                        print_error("Connect DB", e)
                        raise CREDENTIALS_EXCEPTION
    except Exception as e:
        print_error("Try refresh token", e)
        raise CREDENTIALS_EXCEPTION

    print_error("Refresh token", "Something went wrong")
    raise CREDENTIALS_EXCEPTION
