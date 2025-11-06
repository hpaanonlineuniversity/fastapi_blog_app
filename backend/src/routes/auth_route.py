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

# routes/auth_route.py - logout route ကို update

@router.post("/logout")
async def logout(
    request: Request,
    response: Response
):
    """Logout user without requiring authentication"""
    try:
        access_token = None
        refresh_token = request.cookies.get("refresh_token")
        
        print(f"🔍 LOGOUT REQUEST - refresh_token from cookie: {refresh_token is not None}")
        
        # Get access token from header or cookie
        authorization = request.headers.get("authorization")
        if authorization and authorization.startswith("Bearer "):
            access_token = authorization[7:]
            print(f"🔍 Access token from header: {access_token[:20]}...")
        elif "access_token" in request.cookies:
            access_token = request.cookies.get("access_token")
            print(f"🔍 Access token from cookie: {access_token[:20]}...")
        else:
            print("❌ No access token found")
        
        # If we have tokens, try to get user info
        user_id = None
        if access_token:
            try:
                # Use your existing token verification function
                from ..utils.security import verify_access_token  # Use the async function
                payload = await verify_access_token(access_token)
                if payload and "id" in payload:
                    user_id = payload.get("id")
                    print(f"✅ Extracted user_id from token: {user_id}")
                else:
                    print("❌ Could not extract user_id from token")
            except Exception as e:
                print(f"❌ Token verification failed: {e}")
                # Continue with logout even if token is invalid
        
        print(f"🔍 FINAL - user_id: {user_id}, access_token: {access_token is not None}")
        
        # Call controller with available info
        return await auth_controller.logout(
            user_id,  
            access_token, 
            refresh_token, 
            response
        )
    except Exception as e:
        print(f"❌ Logout route error: {e}")
        import traceback
        print(traceback.format_exc())
        # Even if there's an error, clear cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return {"message": "Logged out successfully"}

# routes/auth_route.py (Simple approach)
@router.post("/logout-all")
async def logout_all(
    request: Request,  # ✅ Add Request parameter
    response: Response,
    ##current_user: dict = Depends(get_current_user)
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

@router.post("/github", response_model=dict)
async def github_auth(user_data: UserGoogle, response: Response):
    """Google authentication endpoint"""
    return await auth_controller.github_auth(user_data, response)