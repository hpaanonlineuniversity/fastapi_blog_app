# utils/auth_dependency.py (SIMPLE VERSION - Cookie only)
from fastapi import Depends, HTTPException, status, Request
from .security import verify_access_token

async def get_current_user(request: Request):
    """Dependency to get current user from JWT token in cookies only"""
    
    # ✅ Get token only from cookies
    token = request.cookies.get("access_token")
    
    if not token:
        print("❌ No access_token found in cookies")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required - Please sign in again",
        )
    
    print(f"🔑 Token from cookie: {token[:20]}...")
    
    # ✅ Verify the token
    payload = await verify_access_token(token)
    if not payload:
        print("❌ Token verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token - Please sign in again",
        )
    
    print(f"✅ User authenticated: {payload.get('id')}")
    return payload

# utils/auth_dependency.py ထဲမှာ ဒီ function ကို ထပ်ဖြည့်ပါ
async def get_current_user_optional(request: Request):
    """Optional dependency - returns user if authenticated, None if not"""
    try:
        token = request.cookies.get("access_token")
        if not token:
            return None
        
        payload = await verify_access_token(token)
        return payload if payload else None
    except Exception:
        return None