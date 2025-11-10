# controllers/user_controller.py
from fastapi import HTTPException, status, Depends, Request
from ..models.user_model import UserModel
from ..schemas.user_schema import UserUpdate, UserResponse, UsersResponse, UserUpdateAdmin
from ..utils.security import hash_password
from ..utils.auth_dependency import get_current_user
from datetime import datetime, timedelta
from ..utils.password_policy import PasswordPolicy
from ..utils.security import (
    hash_password,
    revoke_refresh_token,
    blacklist_token
)

class UserController:
    def __init__(self):
        self.user_model = UserModel()

    async def test(self):
        """Test endpoint"""
        return {"message": "API is working!"}

    async def update_user(self, user_id: str, update_data: UserUpdate, current_user: dict):
        """Update user profile"""
        # Check if user is updating their own profile
        if current_user["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to update this user"
            )
        
        update_dict = {}

    
        """Update user with password policy validation"""
        # If password is being updated, validate it
        if update_data.password:
            password_validation = PasswordPolicy.validate_password(update_data.password)
            if not password_validation["is_valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"New password does not meet policy: {', '.join(password_validation['errors'])}"
                )
            
            update_dict["password"] = hash_password(update_data.password)
        
        # Validate and prepare update data
        if update_data.username:
            # Check if username already exists (using await now)
            existing_user = await self.user_model.find_user_by_username(update_data.username)
            if existing_user and str(existing_user["_id"]) != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            update_dict["username"] = update_data.username
        
        if update_data.email:
            # Check if email already exists (using await now)
            existing_user = await self.user_model.find_user_by_email(update_data.email)
            if existing_user and str(existing_user["_id"]) != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            update_dict["email"] = update_data.email
        
            
        
        if update_data.profilePicture:
            update_dict["profilePicture"] = update_data.profilePicture
        
        # Update user in database (using await now)
        if update_dict:
            success = await self.user_model.update_user(user_id, update_dict)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        # Get updated user (using await now)
        updated_user = await self.user_model.find_user_by_id(user_id)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=str(updated_user["_id"]),
            username=updated_user["username"],
            email=updated_user["email"],
            profilePicture=updated_user.get("profilePicture"),
            isAdmin=updated_user.get("isAdmin", False)
        )

    async def delete_user(self, user_id: str, current_user: dict, request: Request = None):
        """Delete user"""
        # Check permissions
        if not current_user["isAdmin"] and current_user["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to delete this user"
            )
        
        try:
            # Step 1: Revoke refresh token from Redis (ဒါက အရေးကြီးဆုံး)
            await revoke_refresh_token(user_id)
            print(f"✅ Revoked refresh tokens for user: {user_id}")

            # Step 2: Try to blacklist tokens if request is available
            if request:
                access_token = request.cookies.get("access_token")
                refresh_token = request.cookies.get("refresh_token")
                
                print(f"🔍 Token extraction - Access: {access_token is not None}, Refresh: {refresh_token is not None}")
                
                # Blacklist access token
                if access_token and access_token != "None":
                    try:
                        print(f"🔍 Blacklisting access token: {access_token[:20]}...")
                        await blacklist_token(access_token, "access", expire_seconds=15*60)
                        print("✅ Access token blacklisted")
                    except Exception as e:
                        print(f"⚠️ Access token blacklist warning: {e}")
                
                # Blacklist refresh token
                if refresh_token and refresh_token != "None":
                    try:
                        print(f"🔍 Blacklisting refresh token: {refresh_token[:20]}...")
                        await blacklist_token(refresh_token, "refresh", expire_seconds=7*24*60*60)
                        print("✅ Refresh token blacklisted")
                    except Exception as e:
                        print(f"⚠️ Refresh token blacklist warning: {e}")
            else:
                print("ℹ️ No request object - skipping token blacklisting")
            
            # Step 3: Delete user from database
            success = await self.user_model.delete_user(user_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            print(f"✅ User {user_id} successfully deleted")
            return {"message": "User has been deleted"}
        
        except Exception as e:
            print(f"❌ Error in delete_user: {e}")
            raise

    async def get_users(self, current_user: dict, start_index: int = 0, limit: int = 9, sort: str = "desc"):
        """Get all users (admin only)"""
        if not current_user["isAdmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to see all users"
            )
        
        sort_direction = 1 if sort == "asc" else -1
        
        # Get users (using await now)
        users = await self.user_model.get_all_users(
            skip=start_index, 
            limit=limit, 
            sort_direction=sort_direction
        )
        
        # Remove password from response
        users_without_password = []
        for user in users:
            users_without_password.append(UserResponse(
                id=str(user["_id"]),
                username=user["username"],
                email=user["email"],
                profilePicture=user.get("profilePicture"),
                isAdmin=user.get("isAdmin", False)
            ))
        
        # Get counts (using await now)
        total_users = await self.user_model.count_users()
        
        # Last month users count
        one_month_ago = datetime.now() - timedelta(days=30)
        last_month_users = await self.user_model.get_users_count_since_date(one_month_ago)
        
        return UsersResponse(
            users=users_without_password,
            totalUsers=total_users,
            lastMonthUsers=last_month_users
        )

    async def get_user(self, user_id: str):
        """Get user by ID"""
        user = await self.user_model.find_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            email=user["email"],
            profilePicture=user.get("profilePicture"),
            isAdmin=user.get("isAdmin", False)
        )

    async def update_user_admin(self, user_id: str, admin_data: UserUpdateAdmin, current_user: dict):
        """Update user admin status (admin only)"""
        # Check if user is admin
        if not current_user["isAdmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to update admin status"
            )
        
        # Prevent self-admin-status change
        if current_user["id"] == user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot change your own admin status"
            )
        
        # Update admin status (using await now)
        success = await self.user_model.update_user(user_id, {"isAdmin": admin_data.isAdmin})
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get updated user (using await now)
        updated_user = await self.user_model.find_user_by_id(user_id)
        return UserResponse(
            id=str(updated_user["_id"]),
            username=updated_user["username"],
            email=updated_user["email"],
            profilePicture=updated_user.get("profilePicture"),
            isAdmin=updated_user.get("isAdmin", False)
        )

# Create controller instance
user_controller = UserController()