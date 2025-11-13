# utils/csrf_dependency.py (Fixed Version with Cookie Check)
from fastapi import Depends, HTTPException, status, Request, Header
from .auth_dependency import get_current_user
from .csrf_security import csrf_protection

async def verify_csrf_token(
    request: Request,
    current_user: dict = Depends(get_current_user),
    x_csrf_token: str = Header(None, alias="X-CSRF-Token")
):
    """CSRF token ကို verify လုပ်မယ် - Cookie ထဲကနေပါစစ်မယ်"""
    
    # GET requests အတွက် CSRF check မလုပ်ပါ
    if request.method in ["GET", "HEAD", "OPTIONS"]:
        return current_user
    
    # CSRF token ကို multiple sources ကနေရှာမယ်
    csrf_token_from_header = x_csrf_token
    csrf_token_from_cookie = request.cookies.get("csrf_token")  # ✅ Cookie ထဲကနေရှာမယ်
    
    # ✅ CSRF token from form data (if exists)
    csrf_token_from_form = None
    try:
        form_data = await request.form()
        csrf_token_from_form = form_data.get("csrf_token")
    except:
        pass
    
    # Determine which CSRF token to use (priority: header > form)
    csrf_token = csrf_token_from_header or csrf_token_from_form
    
    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token is required in header or form data"
        )
    
    # ✅ Verify that cookie CSRF token exists
    if not csrf_token_from_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF cookie is missing"
        )
    
    # ✅ Compare header token with cookie token (Double Submit Pattern)
    if csrf_token != csrf_token_from_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch between header and cookie"
        )
    
    # ✅ CSRF token verify လုပ်မယ် (Redis check)
    is_valid = await csrf_protection.verify_csrf_token(csrf_token, current_user["id"])
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired CSRF token"
        )
    
    return current_user

async def get_csrf_token(current_user: dict = Depends(get_current_user)):
    """CSRF token ရယူဖို့"""
    csrf_token = await csrf_protection.generate_csrf_token(current_user["id"])
    return csrf_token