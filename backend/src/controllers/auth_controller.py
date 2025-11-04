# controllers/auth_controller.py
from fastapi import HTTPException, status
from ..models.user_model import UserModel
from ..schemas.user_schema import UserCreate, UserLogin, UserGoogle, UserResponse
from ..utils.security import hash_password, verify_password, create_jwt_token
import random
import string

class AuthController:
    def __init__(self):
        self.user_model = UserModel()

    async def signup(self, user: UserCreate):
        """Handle user registration"""
        # Check required fields
        if not user.username or not user.email or not user.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All fields are required"
            )
        
        # Check if user already exists (using await now)
        existing_user_email = await self.user_model.find_user_by_email(user.email)
        if existing_user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        existing_user_username = await self.user_model.find_user_by_username(user.username)
        if existing_user_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Hash password
        hashed_password = hash_password(user.password)
        
        # Create user data
        user_data = {
            "username": user.username,
            "email": user.email,
            "password": hashed_password,
            "profilePicture": "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png",
            "isAdmin": False
        }
        
        # Save user (using await now)
        user_id = await self.user_model.create_user(user_data)
        
        return {"message": "Signup successful", "userId": user_id}

    async def signin(self, user: UserLogin):
        """Handle user login"""
        if not user.email or not user.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All fields are required"
            )
        
        # Find user (using await now)
        db_user = await self.user_model.find_user_by_email(user.email)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify password
        if not verify_password(user.password, db_user["password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password"
            )
        
        # Create token
        token = create_jwt_token(str(db_user["_id"]), db_user.get("isAdmin", False))
        
        # Prepare user response (remove password)
        user_response = UserResponse(
            id=str(db_user["_id"]),
            username=db_user["username"],
            email=db_user["email"],
            profilePicture=db_user.get("profilePicture"),
            isAdmin=db_user.get("isAdmin", False)
        )
        
        return {
            "user": user_response.model_dump(),  # Changed from .dict() to .model_dump()
            "token": token
        }

    async def google_auth(self, user_data: UserGoogle):
        """Handle Google authentication"""
        try:
            db_user = await self.user_model.find_user_by_email(user_data.email)
            
            if db_user:
                # User exists - login
                token = create_jwt_token(str(db_user["_id"]), db_user.get("isAdmin", False))
                
                user_response = UserResponse(
                    id=str(db_user["_id"]),
                    username=db_user["username"],
                    email=db_user["email"],
                    profilePicture=db_user.get("profilePicture"),
                    isAdmin=db_user.get("isAdmin", False)
                )
            else:
                # Create new user
                generated_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                hashed_password = hash_password(generated_password)
                
                username = user_data.name.lower().replace(" ", "") + ''.join(random.choices(string.digits, k=4))
                
                new_user_data = {
                    "username": username,
                    "email": user_data.email,
                    "password": hashed_password,
                    "profilePicture": user_data.googlePhotoUrl,
                    "isAdmin": False
                }
                
                user_id = await self.user_model.create_user(new_user_data)
                
                # Get the created user FRESH from database
                db_user = await self.user_model.find_user_by_id(user_id)
                
                if not db_user:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create user"
                    )
                
                token = create_jwt_token(str(db_user["_id"]), db_user.get("isAdmin", False))
                
                user_response = UserResponse(
                    id=str(db_user["_id"]),
                    username=db_user["username"],
                    email=db_user["email"],
                    profilePicture=db_user.get("profilePicture"),
                    isAdmin=db_user.get("isAdmin", False)
                )
            
            return {
                "user": user_response.model_dump(),  # Changed from .dict() to .model_dump()
                "token": token
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Google authentication failed: {str(e)}"
            )

# Create controller instance
auth_controller = AuthController()