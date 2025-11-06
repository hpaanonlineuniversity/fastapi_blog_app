# schemas/user_schema.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

# Existing schemas...
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# ✅ FIXED: Make googlePhotoUrl optional and add provider field
class UserGoogle(BaseModel):
    name: str
    email: EmailStr
    googlePhotoUrl: Optional[str] = None
    photo: Optional[str] = None  # ✅ Add alternative field name
    provider: Optional[str] = "github"  # ✅ Add provider field

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    profilePicture: Optional[str] = None
    isAdmin: bool = False

    class Config:
        from_attributes = True

# ✅ New schemas for user controller
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    profilePicture: Optional[str] = None

    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 6 or len(v) > 40:
                raise ValueError('Username must be between 6 and 40 characters')
            if ' ' in v:
                raise ValueError('Username cannot contain spaces')
            if v != v.lower():
                raise ValueError('Username must be lowercase')
            if not v.isalnum():
                raise ValueError('Username can only contain letters and numbers')
        return v

    @validator('password')
    def validate_password(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class UserUpdateAdmin(BaseModel):
    isAdmin: bool

class UsersResponse(BaseModel):
    users: list[UserResponse]
    totalUsers: int
    lastMonthUsers: int

