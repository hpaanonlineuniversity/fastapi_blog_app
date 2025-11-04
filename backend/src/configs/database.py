# configs/database.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
from ..configs.config import MONGO_USER, MONGO_PASSWORD, MONGO_HOST, MONGO_PORT, MONGO_DBNAME

MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DBNAME}?authSource=admin"

# ✅ Async MongoDB client
client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DBNAME]

def get_database():
    return db

def get_user_collection():
    return db["users"]

def get_post_collection():
    """Get posts collection"""
    return db["posts"]