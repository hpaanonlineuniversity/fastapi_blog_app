from ..models.user_model import UserModel
from ..schemas.user_schema import UserCreate, UserLogin, UserGoogle, UserResponse
from ..utils.security import hash_password, verify_password, create_jwt_token
from ..utils.error_handler import error_handler
import random
import string

class AuthController:
    def __init__(self):
        self.user_model = UserModel()

    async def signup(self, user: UserCreate):
        """Handle user registration"""
        # Check required fields
        if not user.username or not user.email or not user.password:
            error_handler(400, "All fields are required")
        
        # Check if user already exists
        if self.user_model.find_user_by_email(user.email):
            error_handler(400, "Email already exists")
        
        if self.user_model.find_user_by_username(user.username):
            error_handler(400, "Username already exists")
        
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
        
        # Save user
        user_id = self.user_model.create_user(user_data)
        
        return {"message": "Signup successful", "userId": user_id}

    async def signin(self, user: UserLogin):
        """Handle user login"""
        if not user.email or not user.password:
            error_handler(400, "All fields are required")
        
        # Find user
        db_user = self.user_model.find_user_by_email(user.email)
        if not db_user:
            error_handler(404, "User not found")
        
        # Verify password
        if not verify_password(user.password, db_user["password"]):
            error_handler(400, "Invalid password")
        
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
            "user": user_response.dict(),
            "token": token
        }

    async def google_auth(self, user_data: UserGoogle):
        """Handle Google authentication"""
        try:
            db_user = self.user_model.find_user_by_email(user_data.email)
            
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
                
                user_id = self.user_model.create_user(new_user_data)
                
                # Get the created user
                db_user = self.user_model.find_user_by_id(user_id)
                token = create_jwt_token(user_id, False)
                
                user_response = UserResponse(
                    id=user_id,
                    username=username,
                    email=user_data.email,
                    profilePicture=user_data.googlePhotoUrl,
                    isAdmin=False
                )
            
            return {
                "user": user_response.dict(),
                "token": token
            }
            
        except Exception as e:
            error_handler(500, f"Google authentication failed: {str(e)}")

# Create controller instance
auth_controller = AuthController()