# utils/auth_dependency.py (FIXED VERSION)
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .security import verify_access_token

security = HTTPBearer(auto_error=False)  # ✅ Change to auto_error=False

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)  # ✅ This is optional now
):
    """Dependency to get current user from JWT token - checks both header and cookie"""
    token = None
    
    # ✅ FIRST: Try to get token from Authorization header
    if credentials and credentials.credentials:
        token = credentials.credentials
        print(f"🔑 Token from Authorization header: {token[:20]}...")
    
    # ✅ SECOND: Fallback to cookie if no header token
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token")
        print(f"🍪 Token from cookie: {token[:20]}...")
    
    if not token:
        print("❌ No token found in header or cookies")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ✅ Verify the token
    payload = await verify_access_token(token)
    if not payload:
        print("❌ Token verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or blacklisted token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"✅ User authenticated: {payload.get('id')}")
    return payload