# configs/config.py
import os

# MongoDB Configuration
MONGO_USER = os.getenv("MONGO_USER", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "password")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "fast_blog_db")

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-default-secret-key")
JWT_ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET", JWT_SECRET)
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET", JWT_SECRET)
JWT_ACCESS_EXPIRY = os.getenv("JWT_ACCESS_EXPIRY", "15m")
JWT_REFRESH_EXPIRY = os.getenv("JWT_REFRESH_EXPIRY", "7d")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"

# Admin Configuration
ADMIN_USERNAME = os.getenv("USERNAME", "admin")
ADMIN_EMAIL = os.getenv("EMAIL", "admin@gmail.com")
ADMIN_PASSWORD = os.getenv("PASSWORD", "admin")