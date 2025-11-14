# utils/csrf_security.py (Optimized Version)
import secrets
from fastapi import HTTPException, status
from ..configs.redis_client import redis_client

class CSRFProtection:
    def __init__(self):
        # ✅ CSRF token ကို session တစ်ခုလုံးအတွက် သိမ်းထားမယ်
        # Frontend က multiple requests လုပ်နိုင်အောင်
        self.token_expiry = 15 * 60  # 15 minutes (session duration)
    
    async def generate_csrf_token(self, user_id: str = None) -> str:
        """
        CSRF token ဖန်တီးမယ်
        - User-based token: Redis ထဲမှာ သိမ်းမယ်
        - Anonymous token: သိမ်းစရာမလိုဘူး
        """
        csrf_token = secrets.token_urlsafe(32)
        
        if user_id:
            key = f"csrf_token:{user_id}:{csrf_token}"
            success = await redis_client.set_key(key, "valid", self.token_expiry)
            if not success:
                print(f"❌ Failed to store CSRF token in Redis for user: {user_id}")
                raise Exception("Failed to store CSRF token in Redis")
            print(f"✅ Generated CSRF token for user: {user_id} (expires in {self.token_expiry}s)")
        else:
            print(f"✅ Generated anonymous CSRF token")
        
        return csrf_token
    
    async def verify_csrf_token(self, token: str, user_id: str = None) -> bool:
        """
        CSRF token ကို verify လုပ်မယ်
        - ✅ CORRECT: Token ကို မဖျက်ပါနဲ့ (frontend က multiple requests လုပ်နိုင်အောင်)
        - Token ကို session တစ်ခုလုံး သုံးမယ်
        """
        if not token:
            print("❌ CSRF token is missing")
            return False
        
        if user_id:
            key = f"csrf_token:{user_id}:{token}"
            exists = await redis_client.exists_key(key)
            if exists:
                # ✅ CORRECT: Token verified successfully - DON'T DELETE
                # Frontend က同一个 token နဲ့ multiple requests လုပ်နိုင်အောင်
                print(f"✅ CSRF token verified for user: {user_id}")
                return True
            else:
                print(f"❌ CSRF token not found or expired for user: {user_id}")
                return False
        
        # Anonymous requests (no user_id) - basic validation only
        print(f"✅ Anonymous CSRF token verified")
        return True
    
    async def revoke_user_csrf_tokens(self, user_id: str) -> bool:
        """
        User တစ်ယောက်ရဲ့ CSRF token အားလုံးကို ဖျက်မယ်
        - ဒီ function ကို security events မှာပဲသုံးပါ (logout, password change, etc.)
        """
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

    async def refresh_csrf_token(self, old_token: str, user_id: str) -> str:
        """
        CSRF token ကို refresh လုပ်မယ်
        - ဒီ function ကို frontend က token expire ဖြစ်မယ့်အချိန်မှာပဲသုံးပါ
        - Normal requests အတွက် မလိုအပ်ပါ
        """
        try:
            if not user_id:
                raise Exception("User ID is required for token refresh")
            
            # Verify the old token first
            if not await self.verify_csrf_token(old_token, user_id):
                raise Exception("Invalid old CSRF token")
            
            # Revoke old tokens and generate new one
            await self.revoke_user_csrf_tokens(user_id)
            new_token = await self.generate_csrf_token(user_id)
            
            print(f"✅ CSRF token refreshed for user: {user_id}")
            return new_token
            
        except Exception as e:
            print(f"❌ Error refreshing CSRF token for user {user_id}: {e}")
            raise

    async def get_remaining_ttl(self, token: str, user_id: str) -> int:
        """
        CSRF token ရဲ့ remaining TTL ကို ရယူမယ်
        - Frontend က token expire ဖြစ်မယ့်အချိန်ကို သိအောင်
        """
        try:
            if not user_id:
                return self.token_expiry
                
            key = f"csrf_token:{user_id}:{token}"
            ttl = await redis_client.get_ttl(key)
            
            if ttl is not None:
                print(f"ℹ️ CSRF token TTL for user {user_id}: {ttl}s")
                return ttl
            else:
                print(f"❌ CSRF token not found for TTL check: {user_id}")
                return -1
                
        except Exception as e:
            print(f"❌ Error getting CSRF token TTL: {e}")
            return -1

    async def validate_and_renew_token(self, token: str, user_id: str) -> dict:
        """
        CSRF token ကို validate လုပ်ပြီး renew လိုအပ်လားဆိုတာ check လုပ်မယ်
        - Frontend အတွက် convenient function
        """
        try:
            if not user_id:
                return {
                    "valid": True,
                    "needs_refresh": False,
                    "remaining_ttl": self.token_expiry
                }
            
            # Check if token exists and get TTL
            key = f"csrf_token:{user_id}:{token}"
            exists = await redis_client.exists_key(key)
            
            if not exists:
                return {
                    "valid": False,
                    "needs_refresh": True,
                    "remaining_ttl": 0,
                    "message": "CSRF token not found or expired"
                }
            
            # Get remaining TTL
            ttl = await redis_client.get_ttl(key)
            
            # If token expires in less than 2 minutes, suggest refresh
            needs_refresh = ttl is not None and ttl < 120
            
            return {
                "valid": True,
                "needs_refresh": needs_refresh,
                "remaining_ttl": ttl or 0,
                "message": "Token will expire soon" if needs_refresh else "Token is valid"
            }
            
        except Exception as e:
            print(f"❌ Error validating CSRF token: {e}")
            return {
                "valid": False,
                "needs_refresh": True,
                "remaining_ttl": 0,
                "message": f"Validation error: {str(e)}"
            }

    async def bulk_verify_tokens(self, tokens: list, user_id: str) -> dict:
        """
        Multiple CSRF tokens ကို တစ်ခါတည်း verify လုပ်မယ်
        - Batch operations အတွက် useful
        """
        try:
            results = {}
            
            for token in tokens:
                results[token] = await self.verify_csrf_token(token, user_id)
            
            print(f"✅ Bulk verified {len(tokens)} CSRF tokens for user: {user_id}")
            return {
                "success": True,
                "results": results,
                "valid_count": sum(1 for valid in results.values() if valid),
                "invalid_count": sum(1 for valid in results.values() if not valid)
            }
            
        except Exception as e:
            print(f"❌ Error in bulk token verification: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": {}
            }

    # ✅ Security event handlers
    async def on_user_logout(self, user_id: str) -> bool:
        """User logout လုပ်တဲ့အခါ CSRF tokens အားလုံးကို revoke လုပ်မယ်"""
        print(f"🛡️ Security event: User logout - revoking CSRF tokens for user: {user_id}")
        return await self.revoke_user_csrf_tokens(user_id)
    
    async def on_password_change(self, user_id: str) -> bool:
        """Password change လုပ်တဲ့အခါ CSRF tokens အားလုံးကို revoke လုပ်မယ်"""
        print(f"🛡️ Security event: Password change - revoking CSRF tokens for user: {user_id}")
        return await self.revoke_user_csrf_tokens(user_id)
    
    async def on_suspicious_activity(self, user_id: str) -> bool:
        """Suspicious activity ရှိတဲ့အခါ CSRF tokens အားလုံးကို revoke လုပ်မယ်"""
        print(f"🛡️ Security event: Suspicious activity - revoking CSRF tokens for user: {user_id}")
        return await self.revoke_user_csrf_tokens(user_id)
    
    async def on_session_timeout(self, user_id: str) -> bool:
        """Session timeout ဖြစ်တဲ့အခါ CSRF tokens အားလုံးကို revoke လုပ်မယ်"""
        print(f"🛡️ Security event: Session timeout - revoking CSRF tokens for user: {user_id}")
        return await self.revoke_user_csrf_tokens(user_id)

    # ✅ Monitoring and statistics
    async def get_csrf_stats(self, user_id: str = None) -> dict:
        """
        CSRF token statistics ကို ရယူမယ်
        - Monitoring purposes
        """
        try:
            if user_id:
                pattern = f"csrf_token:{user_id}:*"
            else:
                pattern = "csrf_token:*"
            
            # Note: This might be expensive for large datasets
            # In production, you might want to use Redis SCAN
            keys = await redis_client.get_keys(pattern)
            
            stats = {
                "total_tokens": len(keys),
                "user_id": user_id or "all_users",
                "token_expiry": self.token_expiry
            }
            
            print(f"ℹ️ CSRF stats: {stats}")
            return stats
            
        except Exception as e:
            print(f"❌ Error getting CSRF stats: {e}")
            return {
                "error": str(e),
                "total_tokens": 0,
                "user_id": user_id or "all_users"
            }

# Global instance
csrf_protection = CSRFProtection()