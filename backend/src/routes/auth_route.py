from fastapi import APIRouter, Response, Request
from ..models.user_model import UserModel
from ..schemas.user_schema import UserCreate, UserLogin, UserGoogle, UserResponse
from ..utils.security import hash_password, verify_password, create_jwt_token
from ..utils.error_handler import error_handler
import json

router = APIRouter()
user_model = UserModel()

@router.post("/signup", response_model=dict)
async def signup(user: UserCreate):
    # Check required fields
    if not user.username or not user.email or not user.password:
        error_handler(400, "All fields are required")
    
    # Check if user already exists
    if user_model.find_user_by_email(user.email):
        error_handler(400, "Email already exists")
    
    if user_model.find_user_by_username(user.username):
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
    user_id = user_model.create_user(user_data)
    
    return {"message": "Signup successful", "userId": user_id}

@router.post("/signin", response_model=dict)
async def signin(user: UserLogin, response: Response):
    if not user.email or not user.password:
        error_handler(400, "All fields are required")
    
    # Find user
    db_user = user_model.find_user_by_email(user.email)
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
    
    # Set cookie (FastAPI doesn't have built-in cookie parser like Express)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=7*24*60*60,  # 7 days
        samesite="lax"
    )
    
    return {"user": user_response.dict()}

@router.post("/google", response_model=dict)
async def google_auth(user_data: UserGoogle, response: Response):
    try:
        db_user = user_model.find_user_by_email(user_data.email)
        
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
            import random
            import string
            
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
            
            user_id = user_model.create_user(new_user_data)
            
            # Get the created user
            db_user = user_model.find_user_by_id(user_id)
            token = create_jwt_token(user_id, False)
            
            user_response = UserResponse(
                id=user_id,
                username=username,
                email=user_data.email,
                profilePicture=user_data.googlePhotoUrl,
                isAdmin=False
            )
        
        # Set cookie
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=7*24*60*60,
            samesite="lax"
        )
        
        return {"user": user_response.dict()}
        
    except Exception as e:
        error_handler(500, f"Google authentication failed: {str(e)}")