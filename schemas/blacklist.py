from pydantic import BaseModel


class BlacklistBase(BaseModel):
    key: str


class Blacklist(BlacklistBase):
    id: int

    class Config:
        orm_mode = True
