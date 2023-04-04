from fastapi import FastAPI, Request
from utils.jwt import get_current_user_email

api_app = FastAPI()


@api_app.get("/")
def test():
    return {"message": "unprotected api_app endpoint"}


@api_app.get("/protected")
async def test2(request: Request):
    current_email: str = await get_current_user_email(request)
    return {"message": "protected api_app endpoint"}
