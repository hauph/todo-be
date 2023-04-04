from pydantic import BaseModel


class TodoBase(BaseModel):
    description: str


class TodoCreate(TodoBase):
    pass


class Todo(TodoBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
