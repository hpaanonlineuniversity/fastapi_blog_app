from fastapi import APIRouter, Response, Request
from ..controllers.auth_controller import auth_controller
from ..schemas.user_schema import UserCreate, UserLogin, UserGoogle

router = APIRouter()

@router.post("/signup", response_model=dict)
async def signup(user: UserCreate):
    """User registration endpoint"""
    return await auth_controller.signup(user)

@router.post("/signin", response_model=dict)
async def signin(user: UserLogin, response: Response):
    """User login endpoint"""
    result = await auth_controller.signin(user)
    
    # Set cookie
    response.set_cookie(
        key="access_token",
        value=result["token"],
        httponly=True,
        max_age=7*24*60*60,  # 7 days
        samesite="lax"
    )
    
    return {"user": result["user"]}

@router.post("/google", response_model=dict)
async def google_auth(user_data: UserGoogle, response: Response):
    """Google authentication endpoint"""
    result = await auth_controller.google_auth(user_data)
    
    # Set cookie
    response.set_cookie(
        key="access_token",
        value=result["token"],
        httponly=True,
        max_age=7*24*60*60,
        samesite="lax"
    )
    
    return {"user": result["user"]}