from sqlalchemy import Column, Integer, String

from db.database import Base


class Blacklist(Base):
    __tablename__ = "blacklist_keys"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
