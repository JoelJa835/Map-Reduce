from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from schemas import UserRole
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user)
    created_dt = Column(DateTime, default=datetime.utcnow())

