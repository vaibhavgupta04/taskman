from typing import Optional, List
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship

class UserRole(str):
    ADMIN = "admin"
    MEMBER = "member"

# Database Table Model
class User(SQLModel, table=True):
    user_id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    is_active: bool = Field(default=True)
    role: str = Field(default=UserRole.MEMBER)

class UserLogin(SQLModel):
    username: str
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str