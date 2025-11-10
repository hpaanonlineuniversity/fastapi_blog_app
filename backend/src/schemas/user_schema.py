# schemas/user_schema.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import re

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @validator('password')
    def validate_password_strength(cls, v):
        if not v:
            raise ValueError('Password is required')
        
        # Password policy rules
        errors = []
        
        # Minimum length
        if len(v) < 8:
            errors.append('Password must be at least 8 characters long')
        
        # Check for uppercase letters
        if not re.search(r'[A-Z]', v):
            errors.append('Password must contain at least one uppercase letter')
        
        # Check for lowercase letters  
        if not re.search(r'[a-z]', v):
            errors.append('Password must contain at least one lowercase letter')
        
        # Check for numbers
        if not re.search(r'\d', v):
            errors.append('Password must contain at least one number')
        
        # Check for special characters
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            errors.append('Password must contain at least one special character')
        
        if errors:
            raise ValueError('; '.join(errors))
        
        return v

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

# schemas/user_schema.py (update UserUpdate)
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
    def validate_password_update(cls, v):
        if v is not None:
            # Apply the same password policy for updates
            errors = []
            
            if len(v) < 8:
                errors.append('Password must be at least 8 characters long')
            
            if not re.search(r'[A-Z]', v):
                errors.append('Password must contain at least one uppercase letter')
            
            if not re.search(r'[a-z]', v):
                errors.append('Password must contain at least one lowercase letter')
            
            if not re.search(r'\d', v):
                errors.append('Password must contain at least one number')
            
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
                errors.append('Password must contain at least one special character')
            
            if errors:
                raise ValueError('; '.join(errors))
        
        return v

class UserUpdateAdmin(BaseModel):
    isAdmin: bool

class UsersResponse(BaseModel):
    users: list[UserResponse]
    totalUsers: int
    lastMonthUsers: int

