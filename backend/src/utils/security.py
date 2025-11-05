# utils/security.py (Complete corrected version)
import bcrypt
import jwt
from datetime import datetime, timedelta
import re
from ..configs.config import JWT_ACCESS_SECRET, JWT_REFRESH_SECRET, JWT_ACCESS_EXPIRY, JWT_REFRESH_EXPIRY
from ..configs.redis_client import redis_client

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hashed password"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def _parse_jwt_expiry(expiry_string: str) -> timedelta:
    """Parse JWT expiry string like '15m', '7d' into timedelta"""
    match = re.match(r'^(\d+)([mhd])$', expiry_string.lower())
    if not match:
        return timedelta(days=7)  # Default to 7 days
    
    value, unit = match.groups()
    value = int(value)
    
    if unit == 'm':
        return timedelta(minutes=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)
    else:
        return timedelta(days=7)

def create_access_token(user_id: str, is_admin: bool = False) -> str:
    """Create JWT access token"""
    expiry_delta = _parse_jwt_expiry(JWT_ACCESS_EXPIRY)
    payload = {
        "id": user_id,
        "isAdmin": is_admin,
        "type": "access",
        "exp": datetime.utcnow() + expiry_delta
    }
    return jwt.encode(payload, JWT_ACCESS_SECRET, algorithm="HS256")

async def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token and store in Redis"""
    expiry_delta = _parse_jwt_expiry(JWT_REFRESH_EXPIRY)
    payload = {
        "id": user_id,
        "type": "refresh",
        "exp": datetime.utcnow() + expiry_delta
    }
    refresh_token = jwt.encode(payload, JWT_REFRESH_SECRET, algorithm="HS256")
    
    # Store refresh token in Redis with expiry
    expire_seconds = int(expiry_delta.total_seconds())
    success = await redis_client.set_key(f"refresh_token:{user_id}", refresh_token, expire_seconds)
    
    if not success:
        print(f"❌ Failed to store refresh token in Redis for user: {user_id}")
    
    return refresh_token

async def verify_access_token(token: str):
    """Verify JWT access token and check blacklist"""
    # First check if token is blacklisted
    if await is_token_blacklisted(token, "access"):
        print(f"❌ Access token is blacklisted: {token[:20]}...")
        return None
    
    try:
        payload = jwt.decode(token, JWT_ACCESS_SECRET, algorithms=["HS256"])
        if payload.get("type") != "access":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def verify_refresh_token(token: str):
    """Verify JWT refresh token and check blacklist"""
    # First check if token is blacklisted
    if await is_token_blacklisted(token, "refresh"):
        print(f"❌ Refresh token is blacklisted: {token[:20]}...")
        return None
    
    try:
        payload = jwt.decode(token, JWT_REFRESH_SECRET, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            return None
        
        # Check if refresh token exists in Redis
        user_id = payload.get("id")
        stored_token = await redis_client.get_key(f"refresh_token:{user_id}")
        
        if stored_token != token:
            return None
            
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# utils/security.py - blacklist_token function ကို update

async def blacklist_token(token: str, token_type: str = "access", expire_seconds: int = 3600):
    """Add token to blacklist with expiration"""
    if not token or token == "None":
        print(f"❌ Cannot blacklist empty token for type: {token_type}")
        return False
        
    # Create a unique key for blacklisted token
    blacklist_key = f"blacklist:{token_type}:{token}"
    
    print(f"🔍 Attempting to blacklist - Key: {blacklist_key}, Expiry: {expire_seconds}s")
    
    # Store with expiration (default 1 hour for access tokens)
    success = await redis_client.set_key(blacklist_key, "blacklisted", expire_seconds)
    
    if success:
        print(f"✅ Successfully blacklisted {token_type} token: {token[:20]}...")
        # Verify it was actually stored
        exists = await redis_client.exists_key(blacklist_key)
        print(f"✅ Blacklist verification - exists: {exists}")
    else:
        print(f"❌ Failed to blacklist {token_type} token")
    
    return success

async def is_token_blacklisted(token: str, token_type: str = "access") -> bool:
    """Check if token is blacklisted"""
    blacklist_key = f"blacklist:{token_type}:{token}"
    return await redis_client.exists_key(blacklist_key)

async def blacklist_user_tokens(user_id: str, access_token: str, refresh_token: str):
    """Blacklist both access and refresh tokens for a user"""
    # Blacklist access token for 15 minutes (matches access token expiry)
    await blacklist_token(access_token, "access", expire_seconds=15*60)
    
    # Blacklist refresh token for 7 days (matches refresh token expiry) 
    await blacklist_token(refresh_token, "refresh", expire_seconds=7*24*60*60)
    
    print(f"✅ Blacklisted all tokens for user: {user_id}")

async def revoke_refresh_token(user_id: str):
    """Revoke refresh token by deleting from Redis"""
    success = await redis_client.delete_key(f"refresh_token:{user_id}")
    if success:
        print(f"✅ Revoked refresh token for user: {user_id}")
    else:
        print(f"❌ Failed to revoke refresh token for user: {user_id}")

async def revoke_all_user_tokens(user_id: str):
    """Revoke all tokens for a user (logout all devices)"""
    success = await redis_client.delete_key(f"refresh_token:{user_id}")
    if success:
        print(f"✅ Revoked all tokens for user: {user_id}")
    else:
        print(f"❌ Failed to revoke tokens for user: {user_id}")

# Backward compatibility functions
def create_jwt_token(user_id: str, is_admin: bool = False) -> str:
    """Legacy function for backward compatibility"""
    return create_access_token(user_id, is_admin)

def verify_jwt_token(token: str):
    """Legacy function for backward compatibility"""
    # Note: This can't be async for backward compatibility
    # So we'll make a sync version that doesn't check blacklist
    try:
        payload = jwt.decode(token, JWT_ACCESS_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None