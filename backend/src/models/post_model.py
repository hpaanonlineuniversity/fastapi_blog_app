# models/post_model.py
from datetime import datetime
from bson import ObjectId
from typing import Optional, List, Dict, Any

class PostModel:
    def __init__(self):
        from ..configs.database import get_post_collection
        self.collection = get_post_collection()
    
    async def create_post(self, post_data: dict) -> str:
        """Create a new post and return post ID"""
        post_data["createdAt"] = datetime.now()
        post_data["updatedAt"] = datetime.now()
        result = await self.collection.insert_one(post_data)
        return str(result.inserted_id)
    
    async def find_post_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Find post by slug"""
        return await self.collection.find_one({"slug": slug})
    
    async def find_post_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Find post by ID"""
        try:
            return await self.collection.find_one({"_id": ObjectId(post_id)})
        except:
            return None
    
    async def find_post_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Find post by title"""
        return await self.collection.find_one({"title": title})
    
    async def update_post(self, post_id: str, update_data: dict) -> bool:
        """Update post and return success status"""
        update_data["updatedAt"] = datetime.now()
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete post and return success status"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(post_id)})
            return result.deleted_count > 0
        except:
            return False
    
    async def get_posts(
        self, 
        query: dict = None, 
        skip: int = 0, 
        limit: int = 9, 
        sort_direction: int = -1
    ) -> List[Dict[str, Any]]:
        """Get posts with filtering, pagination and sorting"""
        if query is None:
            query = {}
        
        try:
            cursor = self.collection.find(query).sort("updatedAt", sort_direction).skip(skip).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            print(f"Error getting posts: {e}")
            return []
    
    async def count_posts(self, query: dict = None) -> int:
        """Count posts matching query"""
        if query is None:
            query = {}
        
        try:
            return await self.collection.count_documents(query)
        except Exception as e:
            print(f"Error counting posts: {e}")
            return 0
    
    async def get_posts_by_user_id(self, user_id: str, skip: int = 0, limit: int = 9) -> List[Dict[str, Any]]:
        """Get posts by user ID"""
        return await self.get_posts({"userId": user_id}, skip=skip, limit=limit)
    
    async def get_posts_by_category(self, category: str, skip: int = 0, limit: int = 9) -> List[Dict[str, Any]]:
        """Get posts by category"""
        return await self.get_posts({"category": category}, skip=skip, limit=limit)
    
    async def search_posts(self, search_term: str, skip: int = 0, limit: int = 9) -> List[Dict[str, Any]]:
        """Search posts by title or content"""
        query = {
            "$or": [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"content": {"$regex": search_term, "$options": "i"}}
            ]
        }
        return await self.get_posts(query, skip=skip, limit=limit)