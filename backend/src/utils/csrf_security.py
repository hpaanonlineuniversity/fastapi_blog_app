# utils/csrf_security.py (Optimized Version)
import secrets
from fastapi import HTTPException, status
from ..configs.redis_client import redis_client

class CSRFProtection:
    def __init__(self):
        # ✅ CSRF token ကို 15 မိနစ် (access token နဲ့တူအောင်) ပြင်မယ်
        self.token_expiry = 15 * 60  # 15 minutes
    
    async def generate_csrf_token(self, user_id: str = None) -> str:
        """CSRF token ဖန်တီးမယ်"""
        csrf_token = secrets.token_urlsafe(32)
        
        if user_id:
            key = f"csrf_token:{user_id}:{csrf_token}"
            success = await redis_client.set_key(key, "valid", self.token_expiry)
            if not success:
                print(f"❌ Failed to store CSRF token in Redis for user: {user_id}")
                raise Exception("Failed to store CSRF token in Redis")
        
        print(f"✅ Generated CSRF token for user: {user_id} (expires in {self.token_expiry}s)")
        return csrf_token
    
    async def verify_csrf_token(self, token: str, user_id: str = None) -> bool:
        """CSRF token ကို verify လုပ်မယ်"""
        if not token:
            print("❌ CSRF token is missing")
            return False
        
        if user_id:
            key = f"csrf_token:{user_id}:{token}"
            exists = await redis_client.exists_key(key)
            if exists:
                # ✅ Token ကို ဖျက်ပစ်မယ် (one-time use)
                await redis_client.delete_key(key)
                print(f"✅ CSRF token verified and deleted for user: {user_id}")
                return True
            else:
                print(f"❌ CSRF token not found or expired for user: {user_id}")
                return False
        
        return True
    
    async def revoke_user_csrf_tokens(self, user_id: str):
        """User တစ်ယောက်ရဲ့ CSRF token အားလုံးကို ဖျက်မယ်"""
        try:
            if not user_id:
                print("❌ No user_id provided for CSRF token revocation")
                return False
                
            pattern = f"csrf_token:{user_id}:*"
            success = await redis_client.delete_pattern(pattern)
            
            if success:
                print(f"✅ Successfully revoked all CSRF tokens for user: {user_id}")
            else:
                print(f"ℹ️ No CSRF tokens found for user: {user_id}")
                
            return success
        except Exception as e:
            print(f"❌ Error revoking CSRF tokens for user {user_id}: {e}")
            return False

    # ✅ NEW: Auto-cleanup expired CSRF tokens (optional)
    async def cleanup_expired_csrf_tokens(self, user_id: str = None):
        """Expired CSRF tokens တွေကို cleanup လုပ်မယ်"""
        try:
            if user_id:
                pattern = f"csrf_token:{user_id}:*"
            else:
                pattern = "csrf_token:*"
            
            # Redis က automatically TTL ကုန်တဲ့ keys တွေကို ဖျက်သိမ်းပေးတယ်
            # ဒါကြောင့် manual cleanup မလိုအပ်ပါ
            print(f"ℹ️ CSRF tokens auto-cleanup handled by Redis TTL")
            return True
        except Exception as e:
            print(f"❌ Error cleaning up CSRF tokens: {e}")
            return False

csrf_protection = CSRFProtection()