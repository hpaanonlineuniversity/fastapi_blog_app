# models/post_model.py
from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional
from bson import ObjectId

class Post(Document):
    userId: str
    content: str
    title: str = Field(unique=True)
    image: Optional[str] = "https://www.hostinger.com/tutorials/wp-content/uploads/sites/2/2021/09/how-to-write-a-blog-post.png"
    category: Optional[str] = "uncategorized"
    slug: str = Field(unique=True)
    createdAt: Optional[datetime] = datetime.now()
    updatedAt: Optional[datetime] = datetime.now()

    class Settings:
        name = "posts"  # MongoDB collection name
        use_state_management = True

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PostModel:
    def __init__(self):
        from ..configs.database import get_post_collection
        self.collection = get_post_collection()
    
    async def create_post(self, post_data: dict):
        post_data["createdAt"] = datetime.now()
        post_data["updatedAt"] = datetime.now()
        result = await self.collection.insert_one(post_data)
        return str(result.inserted_id)
    
    async def find_post_by_slug(self, slug: str):
        return await self.collection.find_one({"slug": slug})
    
    async def find_post_by_id(self, post_id: str):
        return await self.collection.find_one({"_id": ObjectId(post_id)})
    
    async def update_post(self, post_id: str, update_data: dict):
        update_data["updatedAt"] = datetime.now()
        result = await self.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def delete_post(self, post_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(post_id)})
        return result.deleted_count > 0
    
    async def get_posts(self, query: dict = None, skip: int = 0, limit: int = 9, sort_direction: int = -1):
        if query is None:
            query = {}
        
        cursor = self.collection.find(query).sort("updatedAt", sort_direction).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def count_posts(self, query: dict = None):
        if query is None:
            query = {}
        return await self.collection.count_documents(query)