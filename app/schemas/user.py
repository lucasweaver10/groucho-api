from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(BaseModel):
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr

class User(UserBase):
    id: int
    profile_photo_url: Optional[str] = None
    created_at: datetime
    subscription_status: Optional[str] = None
    lifetime_access: bool = False
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

class UserMeResponse(User):
    note_count: int = 0
    needs_upgrade: bool = False

class AuthResponse(BaseModel):
    msg: str

class TokenData(BaseModel):
    user_id: str