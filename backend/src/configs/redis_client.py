# configs/redis_client.py (Updated)
import redis.asyncio as redis
import json
from .config import REDIS_URL

class RedisClient:
    def __init__(self):
        self.redis_client = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = await redis.from_url(
                REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis_client.ping()
            print("✅ Redis connected successfully")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            self.redis_client = None
            raise e
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def set_key(self, key: str, value: str, expire: int = None):
        """Set key-value pair with optional expiration"""
        try:
            if self.redis_client is None:
                print("❌ Redis client not connected")
                return False
                
            if expire:
                await self.redis_client.setex(key, expire, value)
            else:
                await self.redis_client.set(key, value)
            print(f"✅ Redis SET: {key} = {value[:20]}... (expire: {expire}s)")
            return True
        except Exception as e:
            print(f"❌ Error setting Redis key {key}: {e}")
            return False
    
    async def get_key(self, key: str):
        """Get value by key"""
        try:
            if self.redis_client is None:
                return None
                
            value = await self.redis_client.get(key)
            if value:
                print(f"✅ Redis GET: {key} = {value[:20]}...")
            return value
        except Exception as e:
            print(f"❌ Error getting Redis key {key}: {e}")
            return None
    
    async def delete_key(self, key: str):
        """Delete key"""
        try:
            if self.redis_client is None:
                return False
                
            result = await self.redis_client.delete(key)
            print(f"✅ Redis DELETE: {key}")
            return result > 0
        except Exception as e:
            print(f"❌ Error deleting Redis key {key}: {e}")
            return False
    
    async def exists_key(self, key: str):
        """Check if key exists"""
        try:
            if self.redis_client is None:
                return False
                
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"❌ Error checking Redis key {key}: {e}")
            return False
    
    async def keys(self, pattern: str = "*"):
        """Get all keys matching pattern"""
        try:
            if self.redis_client is None:
                return []
                
            return await self.redis_client.keys(pattern)
        except Exception as e:
            print(f"❌ Error getting Redis keys: {e}")
            return []

# Global Redis client instance
redis_client = RedisClient()