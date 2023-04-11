from fastapi import FastAPI, Request, Body
from starlette.responses import JSONResponse
from utils.jwt import get_current_user_email
from controllers.user import get_user_by_email
from controllers.todo import (
    get_user_todos,
    create_user_todo,
    edit_user_todo,
    delete_user_todo,
)
from utils.db import (
    get_db,
)
from utils.error import print_error
import json

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
        return {
            "result": True,
            "data": todos,
        }
    except Exception as e:
        print_error("Try get all todos", e)
        raise e


@todo_app.post("/todos")
async def create_todo(request: Request, body=Body(..., media_type="application/json")):
    try:
        # Only accept post requests
        if request.method == "POST":
            current_email: str = await get_current_user_email(request)
            db = get_db(request)
            user = get_user_by_email(db, current_email)
            create_user_todo(db, body, user.id)
            return JSONResponse(
                {
                    "result": True,
                }
            )
    except Exception as e:
        print_error("Post todo", e)
        raise e


@todo_app.put("/todos/{id}")
async def edit_todo(
    request: Request, id: int, body=Body(..., media_type="application/json")
):
    try:
        if request.method == "PUT":
            db = get_db(request)
            edit_user_todo(db, id, body)
            return JSONResponse(
                {
                    "result": True,
                }
            )
    except Exception as e:
        print_error("Edit todo", e)
        raise e


@todo_app.delete("/todos")
async def delete_todo(request: Request, body=Body(..., media_type="application/json")):
    list = body["list"]
    if len(list) > 0:
        try:
            if request.method == "DELETE":
                db = get_db(request)
                delete_user_todo(db, list)
                return JSONResponse(
                    {
                        "result": True,
                    }
                )
        except Exception as e:
            print_error("Delete todo", e)
            raise e
    else:
        raise Exception("Nothing to delete")
