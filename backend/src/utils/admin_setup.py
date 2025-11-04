# utils/admin_setup.py (Create new file)
import os
from ..models.user_model import UserModel
from ..utils.security import hash_password

async def setup_admin_user():
    """Setup admin user on application startup"""
    user_model = UserModel()
    
    # Get admin credentials from environment variables
    admin_username = os.getenv("USERNAME", "admin")
    admin_email = os.getenv("EMAIL", "admin@gmail.com")
    admin_password = os.getenv("PASSWORD", "admin")
    
    try:
        # Check if admin already exists by email
        existing_admin_by_email = await user_model.find_user_by_email(admin_email)
        
        # Check if admin already exists by username
        existing_admin_by_username = await user_model.find_user_by_username(admin_username)
        
        if existing_admin_by_email or existing_admin_by_username:
            print("✅ Admin user already exists")
            return
        
        # Create admin user
        hashed_password = hash_password(admin_password)
        
        admin_data = {
            "username": admin_username,
            "email": admin_email,
            "password": hashed_password,
            "profilePicture": "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png",
            "isAdmin": True
        }
        
        admin_id = await user_model.create_user(admin_data)
        
        print("🎉 Admin user created successfully!")
        print(f"📧 Username: {admin_username}")
        print(f"📧 Email: {admin_email}")
        print(f"🔑 Password: {admin_password}")
        print("⚠️  IMPORTANT: Change the password after first login!")
        print(f"🆔 Admin ID: {admin_id}")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")