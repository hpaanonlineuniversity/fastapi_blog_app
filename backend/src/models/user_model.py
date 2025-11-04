# models/user_model.py
from datetime import datetime
from bson import ObjectId
from typing import Optional, List, Dict, Any

class UserModel:
    def __init__(self):
        from ..configs.database import get_user_collection
        self.collection = get_user_collection()
    
    async def create_user(self, user_data: dict) -> str:
        """Create a new user and return user ID"""
        user_data["createdAt"] = datetime.now()
        user_data["updatedAt"] = datetime.now()
        result = await self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    async def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email"""
        return await self.collection.find_one({"email": email})
    
    async def find_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find user by username"""
        return await self.collection.find_one({"username": username})
    
    async def find_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find user by ID"""
        try:
            return await self.collection.find_one({"_id": ObjectId(user_id)})
        except:
            return None
    
    async def update_user(self, user_id: str, update_data: dict) -> bool:
        """Update user and return success status"""
        update_data["updatedAt"] = datetime.now()
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user and return success status"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except:
            return False
    
    async def get_all_users(
        self, 
        skip: int = 0, 
        limit: int = 9, 
        sort_direction: int = -1
    ) -> List[Dict[str, Any]]:
        """Get all users with pagination and sorting"""
        try:
            cursor = self.collection.find().sort("createdAt", sort_direction).skip(skip).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    async def count_users(self, query: dict = None) -> int:
        """Count users matching query"""
        if query is None:
            query = {}
        
        try:
            return await self.collection.count_documents(query)
        except Exception as e:
            print(f"Error counting users: {e}")
            return 0
    
    async def get_users_count_since_date(self, since_date: datetime) -> int:
        """Count users created since specific date"""
        try:
            return await self.collection.count_documents({"createdAt": {"$gte": since_date}})
        except Exception as e:
            print(f"Error counting users since date: {e}")
            return 0