from sqlalchemy.orm import Session

from models import Todo
from schemas.todo import TodoCreate, TodoUpdate
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


def get_user_todos(db: Session, user_id: int):
    return db.query(Todo).filter(Todo.owner_id == user_id).all()


def create_user_todo(db: Session, todo: TodoCreate, user_id: int):
    db_todo = Todo(**todo, owner_id=user_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def edit_user_todo(db: Session, todo_id: int, todo: TodoUpdate):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo:
        for key, value in todo.items():
            setattr(db_todo, key, value)
        db.commit()
        db.refresh(db_todo)
        return db_todo
    else:
        logger.error("Todo not found")
        return None


def delete_user_todo(db: Session, body: list[int]):
    try:
        db.query(Todo).filter(Todo.id.in_(body)).delete(synchronize_session=False)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting todos: {str(e)}")
        return False
