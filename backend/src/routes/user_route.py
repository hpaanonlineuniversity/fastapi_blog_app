# routes/user_route.py
from fastapi import APIRouter, Depends, Query
from ..controllers.user_controller import user_controller
from ..schemas.user_schema import UserResponse, UsersResponse, UserUpdate, UserUpdateAdmin
from ..utils.auth_dependency import get_current_user

router = APIRouter()

@router.get("/test")
async def test():
    """Test endpoint"""
    return await user_controller.test()

@router.put("/update/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    return await user_controller.update_user(user_id, update_data, current_user)

@router.delete("/delete/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete user"""
    return await user_controller.delete_user(user_id, current_user)

@router.post("/signout")
async def signout():
    """Sign out user"""
    return await user_controller.signout()

@router.get("/getusers", response_model=UsersResponse)
async def get_users(
    current_user: dict = Depends(get_current_user),
    start_index: int = Query(0, ge=0),
    limit: int = Query(9, ge=1, le=100),
    sort: str = Query("desc", regex="^(asc|desc)$")
):
    """Get all users (admin only)"""
    return await user_controller.get_users(current_user, start_index, limit, sort)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    return await user_controller.get_user(user_id)

@router.put("/update-admin/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: str,
    admin_data: UserUpdateAdmin,
    current_user: dict = Depends(get_current_user)
):
    """Update user admin status (admin only)"""
    return await user_controller.update_user_admin(user_id, admin_data, current_user)