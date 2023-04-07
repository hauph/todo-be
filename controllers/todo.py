from sqlalchemy.orm import Session

from models.todo import Todo
from models.user import User
from schemas.todo import TodoCreate
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


def create_user_todo(db: Session, todo: TodoCreate, user_id: int):
    db_todo = Todo(**todo.dict(), owner_id=user_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def get_user_todos(db: Session, user_id: int):
    return db.query(Todo).filter(Todo.owner_id == user_id).all()
