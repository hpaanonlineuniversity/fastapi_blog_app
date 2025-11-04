# utils/auth_dependency.py (Updated)
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .security import verify_access_token

security = HTTPBearer()

# utils/auth_dependency.py (Updated)
async def get_current_user(
    request: Request = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Dependency to get current user from JWT token with blacklist check"""
    token = None
    
    # Try to get token from Authorization header first
    if credentials:
        token = credentials.credentials
    # Fallback to cookie
    elif request and "access_token" in request.cookies:
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = await verify_access_token(token)  # ✅ Add await
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or blacklisted token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload