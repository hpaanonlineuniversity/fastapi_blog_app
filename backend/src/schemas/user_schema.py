from pydantic import BaseModel, validator
from typing import Optional
import re

class UserBase(BaseModel):
    username: str
    email: str  # EmailStr အစား str ပြောင်းသုံးမယ်
    
    @validator('email')
    def email_validator(cls, v):
        if not v:
            raise ValueError('Email is required')
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class UserGoogle(BaseModel):
    email: str
    name: str
    googlePhotoUrl: str

class UserResponse(UserBase):
    id: str
    profilePicture: Optional[str] = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
    isAdmin: bool = False
    
    class Config:
        from_attributes = True