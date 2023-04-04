from fastapi import Request

from crud.blacklist import get_blacklist_token
from crud.user import get_user_by_email


def get_db(request: Request):
    return request.state.db


def is_token_blacklisted(request: Request, token: str):
    db = get_db(request)
    db_blacklist_key = get_blacklist_token(db, token)
    return db_blacklist_key


def valid_email_from_db(request: Request, email: str):
    db = get_db(request)
    db_user = get_user_by_email(db, email)
    return db_user
