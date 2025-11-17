# routes/user_route.py (Full Updated Version with CSRF)
from fastapi import APIRouter, Depends, Query, Request, Header
from ..controllers.user_controller import user_controller
from ..schemas.user_schema import UserResponse, UsersResponse, UserUpdate, UserUpdateAdmin
from ..utils.auth_dependency import get_current_user
from ..utils.csrf_dependency import verify_csrf_token, get_csrf_token

router = APIRouter()

@router.get("/test")
async def test():
    """Test endpoint"""
    return await user_controller.test()

@router.put("/update/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    current_user: dict = Depends(verify_csrf_token)  # ✅ CSRF protection
):
    """Update user profile"""
    return await user_controller.update_user(user_id, update_data, current_user)

# routes/user_route.py

@router.delete("/delete/{user_id}")
async def delete_own_account(
    user_id: str,
    request: Request,
    current_user: dict = Depends(verify_csrf_token)
):
    """User ကိုယ်တိုင် ကိုယ့် account ကို delete လုပ်ခြင်း"""
    return await user_controller.delete_own_account(user_id, current_user, request)

@router.delete("/admin/delete/{user_id}")
async def admin_delete_user(
    user_id: str, 
    current_user: dict = Depends(verify_csrf_token)
):
    """Admin က တခြား user ကို delete လုပ်ခြင်း"""
    return await user_controller.admin_delete_user(user_id, current_user)

# Legacy route for backward compatibility
@router.delete("/legacy-delete/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    current_user: dict = Depends(verify_csrf_token)
):
    """Legacy delete endpoint - maintains backward compatibility"""
    return await user_controller.delete_user(user_id, current_user, request)

@router.get("/getusers", response_model=UsersResponse)
async def get_users(
    current_user: dict = Depends(get_current_user),  # ✅ GET request ဖြစ်လို့ CSRF မလိုပါ
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
    current_user: dict = Depends(verify_csrf_token)  # ✅ CSRF protection
):
    """Update user admin status (admin only)"""
    return await user_controller.update_user_admin(user_id, admin_data, current_user)

# ✅ CSRF token endpoint for users
@router.get("/csrf-token")
async def get_user_csrf_token(
    current_user: dict = Depends(get_current_user)
):
    """Get CSRF token for user operations"""
    csrf_token = await get_csrf_token(current_user)
    return csrf_token