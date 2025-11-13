# routes/auth_route.py (Full Updated Version with CSRF)
from fastapi import APIRouter, Response, Request, Cookie, Depends, Header
from ..controllers.auth_controller import auth_controller
from ..schemas.user_schema import UserCreate, UserLogin, UserGoogle
from ..utils.auth_dependency import get_current_user
from ..utils.csrf_dependency import verify_csrf_token, get_csrf_token
from ..utils.password_policy import PasswordPolicy

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
                from ..utils.security import verify_access_token
                payload = await verify_access_token(access_token)
                if payload and "id" in payload:
                    user_id = payload.get("id")
                    print(f"✅ Extracted user_id from token: {user_id}")
                else:
                    print("❌ Could not extract user_id from token")
            except Exception as e:
                print(f"❌ Token verification failed: {e}")
        
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
        response.delete_cookie("csrf_token")  # ✅ CSRF cookie ပါဖျက်မယ်
        return {"message": "Logged out successfully"}

@router.post("/logout-all")
async def logout_all(
    request: Request,
    response: Response,
    current_user: dict = Depends(verify_csrf_token)  # ✅ CSRF protection
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
        access_token,
        response
    )

@router.post("/github", response_model=dict)
async def github_auth(user_data: UserGoogle, response: Response):
    """GitHub authentication endpoint"""
    return await auth_controller.github_auth(user_data, response)

@router.post("/validate-password")
async def validate_password(password: str):
    """Validate password against policy"""
    validation_result = PasswordPolicy.validate_password(password)
    return {
        "is_valid": validation_result["is_valid"],
        "score": validation_result["score"],
        "strength": validation_result["strength"],
        "errors": validation_result["errors"]
    }

@router.get("/generate-password")
async def generate_password():
    """Generate a strong password"""
    strong_password = PasswordPolicy.generate_strong_password()
    return {
        "password": strong_password,
        "validation": PasswordPolicy.validate_password(strong_password)
    }

@router.get("/check-email/{email}")
async def check_email_availability(email: str):
    """Check if email is available"""
    existing_user = await auth_controller.user_model.find_user_by_email(email)
    return {
        "available": not existing_user,
        "message": "Email already exists" if existing_user else "Email is available"
    }

@router.get("/check-username/{username}")
async def check_username_availability(username: str):
    """Check if username is available"""
    existing_user = await auth_controller.user_model.find_user_by_username(username)
    return {
        "available": not existing_user,
        "message": "Username already exists" if existing_user else "Username is available"
    }

# ✅ CSRF token related endpoints
@router.get("/csrf-token")
async def get_csrf_token_endpoint(
    current_user: dict = Depends(get_current_user)
):
    """Get new CSRF token"""
    return await auth_controller.get_csrf_token(current_user["id"])

@router.post("/verify-csrf")
async def verify_csrf_token_endpoint(
    current_user: dict = Depends(verify_csrf_token)  # ✅ This will verify CSRF token
):
    """Verify CSRF token (for testing)"""
    return {
        "message": "CSRF token is valid",
        "user_id": current_user["id"]
    }