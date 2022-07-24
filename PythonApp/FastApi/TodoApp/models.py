from sqlalchemy import Boolean, Column, Integer, String, DateTime, func
from database import Base


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_completed = Column(DateTime(timezone=True), onupdate=func.now())
