# models.py

from sqlalchemy import Boolean, Column, Integer, String
from .database import Base
from pydantic import BaseModel

class User(Base):
    __tablename__ = "plugin_users" # 定义表名

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    subscription_level = Column(String, default="free")

# Pydantic models for request/response validation
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    verification_code: str # 添加验证码字段

class UserInDB(UserBase):
    id: int
    is_active: bool
    subscription_level: str

    class Config:
        orm_mode = True
