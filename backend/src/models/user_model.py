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