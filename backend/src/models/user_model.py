# models/user_model.py
from datetime import datetime
from bson import ObjectId

class UserModel:
    def __init__(self):
        from ..configs.database import get_user_collection
        self.collection = get_user_collection()
    
    def create_user(self, user_data):
        user_data["createdAt"] = datetime.now()
        user_data["updatedAt"] = datetime.now()
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def find_user_by_email(self, email):
        return self.collection.find_one({"email": email})
    
    def find_user_by_username(self, username):
        return self.collection.find_one({"username": username})
    
    def find_user_by_id(self, user_id):
        return self.collection.find_one({"_id": ObjectId(user_id)})
    
    # ✅ New methods for user controller
    def update_user(self, user_id, update_data):
        update_data["updatedAt"] = datetime.now()
        result = self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def delete_user(self, user_id):
        result = self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    
    def get_all_users(self, skip=0, limit=9, sort_direction=-1):
        # Sort by createdAt: -1 for descending, 1 for ascending
        cursor = self.collection.find().sort("createdAt", sort_direction).skip(skip).limit(limit)
        return list(cursor)
    
    def count_users(self, query=None):
        if query:
            return self.collection.count_documents(query)
        return self.collection.count_documents({})
    
    def get_users_count_since_date(self, since_date):
        return self.collection.count_documents({"createdAt": {"$gte": since_date}})