from pydantic import BaseModel
from schemas.todo import Todo


class UserBase(BaseModel):
    email: str


class User(UserBase):
    id: int
    is_active: bool
    todos: list[Todo] = []

    class Config:
        orm_mode = True
