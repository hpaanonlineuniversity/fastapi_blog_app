# controllers/auth_controller.py (CSRF Error Fixed)
from fastapi import HTTPException, status, Response
from ..models.user_model import UserModel
from ..utils.password_policy import PasswordPolicy
from ..schemas.user_schema import UserCreate, UserLogin, UserGoogle, UserResponse
from ..utils.security import (
    hash_password, 
    verify_password, 
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
    revoke_all_user_tokens,
    blacklist_token
)
from ..utils.csrf_security import csrf_protection
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
        
        # Additional password policy check
        password_validation = PasswordPolicy.validate_password(user.password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password does not meet policy: {', '.join(password_validation['errors'])}"
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

    async def signin(self, user: UserLogin, response: Response):
        """Handle user login with refresh tokens and CSRF"""
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
        
        # ✅ CSRF token ဖန်တီးမယ်
        csrf_token = await csrf_protection.generate_csrf_token(user_id)
        
        # Set HTTP-only cookies
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
        
        # ✅ CSRF token ကို cookie (non-httpOnly) အဖြစ်ထည့်မယ်
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,
            secure=False,
            samesite="lax",
            max_age=1 * 60
        )
        
        # Prepare user response
        user_response = UserResponse(
            id=user_id,
            username=db_user["username"],
            email=db_user["email"],
            profilePicture=db_user.get("profilePicture"),
            isAdmin=db_user.get("isAdmin", False)
        )
        
        return {
            "message": "Login successful",
            "user": user_response.model_dump(),
            "csrfToken": csrf_token
        }

    async def refresh_tokens(self, refresh_token: str, response: Response):
        """Refresh access token using refresh token"""
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token required"
            )
        
        payload = await verify_refresh_token(refresh_token)
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
        new_refresh_token = await create_refresh_token(user_id)
        
        # ✅ New CSRF token ပါထုတ်ပေးမယ်
        new_csrf_token = await csrf_protection.generate_csrf_token(user_id)
        
        # Set new cookies
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
        
        # ✅ CSRF cookie ကိုပါ update လုပ်မယ်
        response.set_cookie(
            key="csrf_token",
            value=new_csrf_token,
            httponly=False,
            secure=False,
            samesite="lax",
            max_age=1 * 60
        )
        
        return {
            "message": "Tokens refreshed successfully",
            "csrfToken": new_csrf_token
        }

    async def logout(self, user_id: str, access_token: str, refresh_token: str, response: Response):
        """Logout user - handle all cases safely"""
        print(f"🔍 LOGOUT DEBUG - user_id: {user_id}, access_token: {access_token is not None}, refresh_token: {refresh_token is not None}")
        
        try:
            # Only revoke tokens if we have valid user_id
            if user_id and user_id != "None":
                print(f"✅ Processing token revocation for user: {user_id}")
                
                try:
                    # Revoke refresh token from Redis
                    await revoke_refresh_token(user_id)
                    print(f"✅ Revoked refresh tokens for user: {user_id}")
                except Exception as e:
                    print(f"❌ Revoke refresh token failed: {e}")
                
                # ✅ CSRF tokens အားလုံးကိုဖျက်မယ် (with error handling)
                try:
                    csrf_success = await csrf_protection.revoke_user_csrf_tokens(user_id)
                    if csrf_success:
                        print(f"✅ Revoked CSRF tokens for user: {user_id}")
                    else:
                        print(f"⚠️ No CSRF tokens found for user: {user_id}")
                except Exception as e:
                    print(f"❌ Revoke CSRF tokens failed: {e}")
                    # Continue with logout even if CSRF revocation fails
                
                # Blacklist both tokens if we have them
                try:
                    if access_token and access_token != "None":
                        success = await blacklist_token(access_token, "access", expire_seconds=15*60)
                        print(f"✅ Access token blacklist result: {success}")
                except Exception as e:
                    print(f"❌ Blacklist access token failed: {e}")
                    
                try:
                    if refresh_token and refresh_token != "None":
                        success = await blacklist_token(refresh_token, "refresh", expire_seconds=7*24*60*60)
                        print(f"✅ Refresh token blacklist result: {success}")
                except Exception as e:
                    print(f"❌ Blacklist refresh token failed: {e}")
            else:
                print("❌ No valid user_id provided, skipping token revocation")
            
            # Always clear cookies regardless of authentication status
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            response.delete_cookie("csrf_token")
            
            print("✅ All cookies cleared successfully")
            return {"message": "Logged out successfully"}
            
        except Exception as e:
            print(f"❌ Logout error: {e}")
            import traceback
            print(traceback.format_exc())
            # Even if there's an error, clear cookies
            response.delete_cookie("access_token") 
            response.delete_cookie("refresh_token")
            response.delete_cookie("csrf_token")
            return {"message": "Logged out successfully"}

    async def logout_all_devices(self, user_id: str, access_token: str, response: Response):
        """Logout user from all devices and blacklist current tokens"""
        # Revoke all refresh tokens for user
        await revoke_all_user_tokens(user_id)
        
        # ✅ CSRF tokens အားလုံးကိုဖျက်မယ်
        await csrf_protection.revoke_user_csrf_tokens(user_id)
        
        # Blacklist the current access token (if provided)
        if access_token:
            await blacklist_token(access_token, "access", expire_seconds=15*60)
            print(f"✅ Blacklisted current access token during logout-all")
        
        # Clear cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        response.delete_cookie("csrf_token")
        
        return {"message": "Logged out from all devices successfully"}

    async def github_auth(self, user_data: UserGoogle, response: Response):
        """Handle GitHub authentication"""
        try:
            # Check if user exists with this email
            db_user = await self.user_model.find_user_by_email(user_data.email)
            
            if db_user:
                print(f"✅ User found: {db_user['email']} - Logging in")
                # User exists - login
                access_token = create_access_token(str(db_user["_id"]), db_user.get("isAdmin", False))
                refresh_token = await create_refresh_token(str(db_user["_id"]))
                
                # ✅ CSRF token ဖန်တီးမယ်
                csrf_token = await csrf_protection.generate_csrf_token(str(db_user["_id"]))
                
                user_response = UserResponse(
                    id=str(db_user["_id"]),
                    username=db_user["username"],
                    email=db_user["email"],
                    profilePicture=db_user.get("profilePicture"),
                    isAdmin=db_user.get("isAdmin", False)
                )
            else:
                print(f"🆕 Creating new user: {user_data.email}")
                # Create new user
                generated_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                hashed_password = hash_password(generated_password)
                
                # Username generation with retry logic
                base_username = user_data.name.lower().replace(" ", "").replace(".", "")[:15]
                username = base_username
                counter = 1
                
                while await self.user_model.find_user_by_username(username):
                    username = f"{base_username}{counter}"
                    counter += 1
                    if counter > 100:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Could not generate unique username"
                        )
                
                new_user_data = {
                    "username": username,
                    "email": user_data.email,
                    "password": hashed_password,
                    "profilePicture": user_data.googlePhotoUrl or "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png",
                    "isAdmin": False
                }
                
                user_id = await self.user_model.create_user(new_user_data)
                db_user = await self.user_model.find_user_by_id(user_id)
                
                if not db_user:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create user"
                    )
                
                access_token = create_access_token(str(db_user["_id"]), db_user.get("isAdmin", False))
                refresh_token = await create_refresh_token(str(db_user["_id"]))
                csrf_token = await csrf_protection.generate_csrf_token(str(db_user["_id"]))
                
                user_response = UserResponse(
                    id=str(db_user["_id"]),
                    username=db_user["username"],
                    email=db_user["email"],
                    profilePicture=db_user.get("profilePicture"),
                    isAdmin=db_user.get("isAdmin", False)
                )
            
            # Set cookies
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
            
            response.set_cookie(
                key="csrf_token",
                value=csrf_token,
                httponly=False,
                secure=False,
                samesite="lax",
                max_age=1 * 60
            )
            
            return {
                "message": "GitHub authentication successful",
                "user": user_response.model_dump(),
                "csrfToken": csrf_token
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ GitHub auth error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"GitHub authentication failed: {str(e)}"
            )

    async def get_csrf_token(self, user_id: str):
        """Get new CSRF token"""
        csrf_token = await csrf_protection.generate_csrf_token(user_id)
        return {"csrfToken": csrf_token}

# Create controller instance
auth_controller = AuthController()