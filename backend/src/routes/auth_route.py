# routes/auth_route.py (Updated)
from fastapi import APIRouter, Response, Request, Cookie, Depends
from ..controllers.auth_controller import auth_controller
from ..schemas.user_schema import UserCreate, UserLogin, UserGoogle
from ..utils.auth_dependency import get_current_user

router = APIRouter()

@router.post("/signup", response_model=dict)
async def signup(user: UserCreate):
    """User registration endpoint"""
    return await auth_controller.signup(user)

@router.post("/signin", response_model=dict)
async def signin(user: UserLogin, response: Response):
    """User login endpoint"""
    return await auth_controller.signin(user, response)

@router.post("/refresh", response_model=dict)
async def refresh_tokens(
    response: Response,
    refresh_token: str = Cookie(None, alias="refresh_token")
):
    """Refresh access token"""
    return await auth_controller.refresh_tokens(refresh_token, response)

# routes/auth_route.py (Update logout endpoints)
@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user)
):
    """Logout user"""
    access_token = None
    refresh_token = request.cookies.get("refresh_token")
    
    # Get access token from header or cookie
    authorization = request.headers.get("authorization")
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization[7:]
    elif "access_token" in request.cookies:
        access_token = request.cookies.get("access_token")
    
    return await auth_controller.logout(
        current_user["id"], 
        access_token, 
        refresh_token, 
        response
    )

# routes/auth_route.py (Simple approach)
@router.post("/logout-all")
async def logout_all(
    request: Request,  # ✅ Add Request parameter
    response: Response,
    current_user: dict = Depends(get_current_user)
):
    """Logout user from all devices"""
    # Get current access token to blacklist it
    access_token = None
    authorization = request.headers.get("authorization")
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization[7:]
    elif "access_token" in request.cookies:
        access_token = request.cookies.get("access_token")
    
    return await auth_controller.logout_all_devices(
        current_user["id"], 
        access_token,  # ✅ Pass access token to blacklist
        response
    )

@router.post("/google", response_model=dict)
async def google_auth(user_data: UserGoogle, response: Response):
    """Google authentication endpoint"""
    return await auth_controller.google_auth(user_data, response)