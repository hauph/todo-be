from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    remind_at = Column(DateTime, index=True)
    description = Column(String, index=True, nullable=False)
    completed = Column(Boolean, index=True, default=False, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, onupdate=func.current_timestamp())
    message_id = Column(String, index=True)

    owner = relationship("User", back_populates="todos")

    def __repr__(self) -> str:
        return f"Todo(id={self.id}, remind_at={self.remind_at}, description={self.description}, completed={self.completed}, owner_id={self.owner_id})"
