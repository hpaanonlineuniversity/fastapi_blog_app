# models/comment_model.py
from datetime import datetime
from bson import ObjectId
from typing import List, Dict, Any, Optional

class CommentModel:
    def __init__(self):
        from ..configs.database import get_comment_collection
        self.collection = get_comment_collection()
    
    async def create_comment(self, comment_data: dict) -> str:
        """Create a new comment and return comment ID"""
        comment_data["createdAt"] = datetime.now()
        comment_data["updatedAt"] = datetime.now()
        result = await self.collection.insert_one(comment_data)
        return str(result.inserted_id)
    
    async def find_comment_by_id(self, comment_id: str) -> Optional[Dict[str, Any]]:
        """Find comment by ID"""
        try:
            return await self.collection.find_one({"_id": ObjectId(comment_id)})
        except:
            return None
    
    async def get_comments_by_post_id(self, post_id: str, sort_direction: int = -1) -> List[Dict[str, Any]]:
        """Get comments by post ID"""
        try:
            cursor = self.collection.find({"postId": post_id}).sort("createdAt", sort_direction)
            return await cursor.to_list(length=None)
        except Exception as e:
            print(f"Error getting comments by post ID: {e}")
            return []
    
    async def update_comment(self, comment_id: str, update_data: dict) -> bool:
        """Update comment and return success status"""
        update_data["updatedAt"] = datetime.now()
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(comment_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    async def delete_comment(self, comment_id: str) -> bool:
        """Delete comment and return success status"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(comment_id)})
            return result.deleted_count > 0
        except:
            return False
    
    async def get_all_comments(
        self, 
        skip: int = 0, 
        limit: int = 9, 
        sort_direction: int = -1
    ) -> List[Dict[str, Any]]:
        """Get all comments with pagination and sorting"""
        try:
            cursor = self.collection.find().sort("createdAt", sort_direction).skip(skip).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            print(f"Error getting all comments: {e}")
            return []
    
    async def count_comments(self, query: dict = None) -> int:
        """Count comments matching query"""
        if query is None:
            query = {}
        
        try:
            return await self.collection.count_documents(query)
        except Exception as e:
            print(f"Error counting comments: {e}")
            return 0
    
    async def get_comments_count_since_date(self, since_date: datetime) -> int:
        """Count comments created since specific date"""
        try:
            return await self.collection.count_documents({"createdAt": {"$gte": since_date}})
        except Exception as e:
            print(f"Error counting comments since date: {e}")
            return 0