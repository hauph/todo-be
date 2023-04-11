from pydantic import BaseModel
from datetime import datetime


class TodoBase(BaseModel):
    description: str
    remind_at: datetime
    completed: bool


class TodoCreate(TodoBase):
    pass


class TodoUpdate(TodoBase):
    description: str | None
    remind_at: datetime | None
    completed: bool | None


class Todo(TodoBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
