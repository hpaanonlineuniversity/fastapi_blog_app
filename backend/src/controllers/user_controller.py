# controllers/user_controller.py
from fastapi import HTTPException, status, Depends
from ..models.user_model import UserModel
from ..schemas.user_schema import UserUpdate, UserResponse, UsersResponse, UserUpdateAdmin
from ..utils.security import hash_password, verify_password
from ..utils.auth_dependency import get_current_user
from datetime import datetime, timedelta

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
        
        # Validate and prepare update data
        if update_data.username:
            # Check if username already exists
            existing_user = self.user_model.find_user_by_username(update_data.username)
            if existing_user and str(existing_user["_id"]) != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            update_dict["username"] = update_data.username
        
        if update_data.email:
            # Check if email already exists
            existing_user = self.user_model.find_user_by_email(update_data.email)
            if existing_user and str(existing_user["_id"]) != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            update_dict["email"] = update_data.email
        
        if update_data.password:
            update_dict["password"] = hash_password(update_data.password)
        
        if update_data.profilePicture:
            update_dict["profilePicture"] = update_data.profilePicture
        
        # Update user in database
        if update_dict:
            success = self.user_model.update_user(user_id, update_dict)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        # Get updated user
        updated_user = self.user_model.find_user_by_id(user_id)
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

    async def delete_user(self, user_id: str, current_user: dict):
        """Delete user"""
        # Check permissions
        if not current_user["isAdmin"] and current_user["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to delete this user"
            )
        
        success = self.user_model.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User has been deleted"}

    async def signout(self):
        """Sign out user"""
        return {"message": "User has been signed out"}

    async def get_users(self, current_user: dict, start_index: int = 0, limit: int = 9, sort: str = "desc"):
        """Get all users (admin only)"""
        if not current_user["isAdmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to see all users"
            )
        
        sort_direction = 1 if sort == "asc" else -1
        
        # Get users
        users = self.user_model.get_all_users(
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
        
        # Get counts
        total_users = self.user_model.count_users()
        
        # Last month users count
        one_month_ago = datetime.now() - timedelta(days=30)
        last_month_users = self.user_model.get_users_count_since_date(one_month_ago)
        
        return UsersResponse(
            users=users_without_password,
            totalUsers=total_users,
            lastMonthUsers=last_month_users
        )

    async def get_user(self, user_id: str):
        """Get user by ID"""
        user = self.user_model.find_user_by_id(user_id)
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
        
        # Update admin status
        success = self.user_model.update_user(user_id, {"isAdmin": admin_data.isAdmin})
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get updated user
        updated_user = self.user_model.find_user_by_id(user_id)
        return UserResponse(
            id=str(updated_user["_id"]),
            username=updated_user["username"],
            email=updated_user["email"],
            profilePicture=updated_user.get("profilePicture"),
            isAdmin=updated_user.get("isAdmin", False)
        )

# Create controller instance
user_controller = UserController()