from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class UserBase(BaseModel):
    username: str
    email: str
    role: UserRole = UserRole.user

class UserCreate(UserBase):
    password: str


class User(UserBase):
    created_dt: datetime

    class Config:
        orm_mode = True