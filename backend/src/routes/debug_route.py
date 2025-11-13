# routes/debug_route.py (Create new file)
## ဒီ debug endpoints တွေက development အတွက်ပဲသုံးတာဖြစ်ပြီး production မှာ disable လုပ်ရမှာပါ

from fastapi import APIRouter
from ..configs.redis_client import redis_client

router = APIRouter()

@router.get("/redis-keys")
async def get_redis_keys():
    """Debug endpoint to check Redis keys"""
    try:
        keys = await redis_client.keys("*")
        key_values = {}
        
        for key in keys:
            value = await redis_client.get_key(key)
            key_values[key] = value
        
        return {
            "keys_count": len(keys),
            "keys": keys,
            "key_values": key_values
        }
    except Exception as e:
        return {"error": str(e)}

# routes/debug_route.py (Add blacklist debug)
@router.get("/blacklist-status")
async def get_blacklist_status(token: str):
    """Check if a token is blacklisted"""
    access_blacklisted = await is_token_blacklisted(token, "access")
    refresh_blacklisted = await is_token_blacklisted(token, "refresh")
    
    return {
        "token": f"{token[:20]}...",
        "access_blacklisted": access_blacklisted,
        "refresh_blacklisted": refresh_blacklisted
    }

@router.get("/redis-stats")
async def get_redis_stats():
    """Get Redis statistics"""
    try:
        all_keys = await redis_client.keys("*")
        blacklisted_keys = await redis_client.keys("blacklist:*")
        refresh_keys = await redis_client.keys("refresh_token:*")
        
        return {
            "total_keys": len(all_keys),
            "blacklisted_tokens": len(blacklisted_keys),
            "active_refresh_tokens": len(refresh_keys),
            "blacklisted_keys": blacklisted_keys,
            "refresh_keys": refresh_keys
        }
    except Exception as e:
        return {"error": str(e)}

