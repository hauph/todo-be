from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from utils.jwt import get_current_user_email
from controllers.user import get_user_by_email
from controllers.todo import get_user_todos
from utils.db import (
    get_db,
)
from utils.error import print_error

import logging

todo_app = FastAPI()

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


@todo_app.get("/todos")
async def get_all_todos(request: Request):
    try:
        current_email: str = await get_current_user_email(request)
        db = get_db(request)
        user = get_user_by_email(db, current_email)
        todos = get_user_todos(db, user.id)
        return JSONResponse(
            {
                "result": True,
                "data": todos,
            }
        )
    except Exception as e:
        print_error("Try get all todos", e)
        raise e
