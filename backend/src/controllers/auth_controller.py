# controllers/auth_controller.py (Correct imports)
from fastapi import HTTPException, status, Response
from ..models.user_model import UserModel
from ..schemas.user_schema import UserCreate, UserLogin, UserGoogle, UserResponse
from ..utils.security import (
    hash_password, 
    verify_password, 
    create_access_token,  # ✅ This should work now
    create_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
    revoke_all_user_tokens,
    blacklist_token,  # ✅ Add this
    blacklist_user_tokens  # ✅ Add this
)
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
        
        # Check if user already exists
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
        
        # Save user
        user_id = await self.user_model.create_user(user_data)
        
        return {"message": "Signup successful", "userId": user_id}

        # controllers/auth_controller.py (Updated - Remove tokens from response)
    async def signin(self, user: UserLogin, response: Response):
        """Handle user login with refresh tokens - Cookies only"""
        if not user.email or not user.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All fields are required"
            )
        
        # Find user
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
        
        user_id = str(db_user["_id"])
        
        # Create tokens
        access_token = create_access_token(user_id, db_user.get("isAdmin", False))
        refresh_token = await create_refresh_token(user_id)
        
        # Set HTTP-only cookies ONLY (no tokens in response)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production
            samesite="lax",
            max_age=15 * 60  # 15 minutes
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # Set to True in production
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        # Prepare user response (NO tokens in response)
        user_response = UserResponse(
            id=user_id,
            username=db_user["username"],
            email=db_user["email"],
            profilePicture=db_user.get("profilePicture"),
            isAdmin=db_user.get("isAdmin", False)
        )
        
        return {
            "message": "Login successful",
            "user": user_response.model_dump()
            # ✅ No access_token or refresh_token in response
        }
    

    async def refresh_tokens(self, refresh_token: str, response: Response):
        """Refresh access token using refresh token - Cookies only"""
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token required"
            )
        
        payload = await verify_refresh_token(refresh_token)  # ✅ Add await
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        user_id = payload.get("id")
        user = await self.user_model.find_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create new tokens
        new_access_token = create_access_token(user_id, user.get("isAdmin", False))
        new_refresh_token = await create_refresh_token(user_id)  # ✅ Add await
        
        # Set new cookies ONLY (no tokens in response)
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=15 * 60
        )
        
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60
        )
        
        return {
            "message": "Tokens refreshed successfully"
            # ✅ No tokens in response
        }                       

    # controllers/auth_controller.py (Update logout methods)
    async def logout(self, user_id: str, access_token: str, refresh_token: str, response: Response):
        """Logout user by revoking and blacklisting tokens"""
        # Revoke refresh token from Redis
        await revoke_refresh_token(user_id)
        
        # Blacklist both tokens
        await blacklist_user_tokens(user_id, access_token, refresh_token)
        
        # Clear cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        
        return {"message": "Logged out successfully"}

    # controllers/auth_controller.py (Simple approach)
    async def logout_all_devices(self, user_id: str, access_token: str, response: Response):
        """Logout user from all devices and blacklist current tokens"""
        # Revoke all refresh tokens for user (this prevents new access tokens)
        await revoke_all_user_tokens(user_id)
        
        # Blacklist the current access token (if provided)
        if access_token:
            await blacklist_token(access_token, "access", expire_seconds=15*60)
            print(f"✅ Blacklisted current access token during logout-all")
        
        # Clear cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        
        return {"message": "Logged out from all devices successfully"}

    async def google_auth(self, user_data: UserGoogle, response: Response):
        """Handle Google authentication with tokens - Cookies only"""
        try:
            db_user = await self.user_model.find_user_by_email(user_data.email)
            
            if db_user:
                # User exists - login
                access_token = create_access_token(str(db_user["_id"]), db_user.get("isAdmin", False))
                refresh_token = await create_refresh_token(str(db_user["_id"]))  # ✅ Add await
                
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
                
                # Get the created user
                db_user = await self.user_model.find_user_by_id(user_id)
                
                if not db_user:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create user"
                    )
                
                access_token = create_access_token(str(db_user["_id"]), db_user.get("isAdmin", False))
                refresh_token = await create_refresh_token(str(db_user["_id"]))  # ✅ Add await
                
                user_response = UserResponse(
                    id=str(db_user["_id"]),
                    username=db_user["username"],
                    email=db_user["email"],
                    profilePicture=db_user.get("profilePicture"),
                    isAdmin=db_user.get("isAdmin", False)
                )
            
            # Set cookies ONLY (no tokens in response)
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=15 * 60
            )
            
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=7 * 24 * 60 * 60
            )
            
            return {
                "message": "Google authentication successful",
                "user": user_response.model_dump()
                # ✅ No tokens in response
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