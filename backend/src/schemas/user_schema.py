from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserGoogle(BaseModel):
    email: EmailStr
    name: str
    googlePhotoUrl: str

class UserResponse(UserBase):
    id: str
    profilePicture: Optional[str] = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
    isAdmin: bool = False
    
    class Config:
        from_attributes = True