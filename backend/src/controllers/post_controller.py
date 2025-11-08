# controllers/post_controller.py
from fastapi import HTTPException, status
from ..models.post_model import PostModel
from ..schemas.post_schema import PostCreate, PostUpdate, PostResponse, PostsResponse
from ..utils.auth_dependency import get_current_user
import re
from datetime import datetime, timedelta
from bson import ObjectId
from bson.errors import InvalidId

class PostController:
    def __init__(self):
        self.post_model = PostModel()

    def _generate_slug(self, title: str) -> str:
        """Generate slug from title"""
        # Fix: Python string operations are different from JavaScript
        slug = title.replace(' ', '-').lower()
        slug = re.sub(r'[^a-zA-Z0-9-]', '', slug)
        return slug

    async def create_post(self, post_data: PostCreate, current_user: dict):
        """Create a new post (Admin only)"""
        # Check if user is admin
        if not current_user["isAdmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to create a post"
            )
        
        # Validate required fields
        if not post_data.title or not post_data.content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide all required fields"
            )
        
        # Check if title already exists
        existing_post_by_title = await self.post_model.find_post_by_title(post_data.title)
        if existing_post_by_title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post title already exists"
            )
        
        # Generate slug
        slug = self._generate_slug(post_data.title)
        
        # Check if slug already exists and make it unique
        existing_post_by_slug = await self.post_model.find_post_by_slug(slug)
        if existing_post_by_slug:
            slug = f"{slug}-{int(datetime.now().timestamp())}"
        
        # Create post data
        post_dict = {
            "userId": current_user["id"],
            "title": post_data.title,
            "content": post_data.content,
            "image": post_data.image or "https://www.hostinger.com/tutorials/wp-content/uploads/sites/2/2021/09/how-to-write-a-blog-post.png",
            "category": post_data.category or "uncategorized",
            "slug": slug
        }
        
        # Save post
        post_id = await self.post_model.create_post(post_dict)
        
        # Get the created post
        new_post = await self.post_model.find_post_by_id(post_id)
        if not new_post:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create post"
            )
        
        return PostResponse(
            id=str(new_post["_id"]),
            userId=new_post["userId"],
            title=new_post["title"],
            content=new_post["content"],
            image=new_post.get("image"),
            category=new_post.get("category", "uncategorized"),
            slug=new_post["slug"],
            createdAt=new_post.get("createdAt"),
            updatedAt=new_post.get("updatedAt")
        )

    async def get_posts(
            self,
            userId: str = None,
            category: str = None,
            slug: str = None,
            postId: str = None,
            searchTerm: str = None,
            startIndex: int = 0,
            limit: int = 9,
            order: str = "desc"
            ):
        
        """Get posts with filtering and pagination"""
        # Build query
        query = {}
        
        if userId:
            query["userId"] = userId
        
        if category:
            query["category"] = category
        
        if slug:
            query["slug"] = slug
        
        if postId:
            try:
                # ObjectId conversion ကို သေချာလုပ်ပါ
                query["_id"] = ObjectId(postId)
            except InvalidId:
                # Invalid ID ဆိုရင် empty result ပြန်ပါ
                return PostsResponse(posts=[], totalPosts=0, lastMonthPosts=0)
        
        if searchTerm:
            query["$or"] = [
                {"title": {"$regex": searchTerm, "$options": "i"}},
                {"content": {"$regex": searchTerm, "$options": "i"}}
            ]
        
        
        # Sort direction
        sort_direction = 1 if order == "asc" else -1
        
        # Get posts
        posts = await self.post_model.get_posts(
            query=query,
            skip=startIndex,
            limit=limit,
            sort_direction=sort_direction
        )
        
        # Convert to response format
        posts_response = []
        for post in posts:
            posts_response.append(PostResponse(
                id=str(post["_id"]),
                userId=post["userId"],
                title=post["title"],
                content=post["content"],
                image=post.get("image"),
                category=post.get("category", "uncategorized"),
                slug=post["slug"],
                createdAt=post.get("createdAt"),
                updatedAt=post.get("updatedAt")
            ))
        
        # Get counts
        total_posts = await self.post_model.count_posts()
        
        # Last month posts count
        one_month_ago = datetime.now() - timedelta(days=30)
        last_month_posts = await self.post_model.count_posts({
            "createdAt": {"$gte": one_month_ago}
        })
        
        return PostsResponse(
            posts=posts_response,
            totalPosts=total_posts,
            lastMonthPosts=last_month_posts
        )

    async def delete_post(self, post_id: str, user_id: str, current_user: dict):
        """Delete a post"""
        # Check permissions
        if not current_user["isAdmin"] and current_user["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to delete this post"
            )
        
        # Check if post exists
        post = await self.post_model.find_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Verify post belongs to user (if not admin)
        if not current_user["isAdmin"] and post["userId"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to delete this post"
            )
        
        # Delete post
        success = await self.post_model.delete_post(post_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete post"
            )
        
        return {"message": "The post has been deleted"}

    async def update_post(
        self, 
        post_id: str, 
        user_id: str, 
        update_data: PostUpdate, 
        current_user: dict
    ):
        """Update a post"""
        # Check permissions
        if not current_user["isAdmin"] and current_user["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to update this post"
            )
        
        # Check if post exists
        post = await self.post_model.find_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Verify post belongs to user (if not admin)
        if not current_user["isAdmin"] and post["userId"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to update this post"
            )
        
        # Prepare update data
        update_dict = {}
        if update_data.title is not None:
            # Check if new title already exists (excluding current post)
            existing_post = await self.post_model.find_post_by_title(update_data.title)
            if existing_post and str(existing_post["_id"]) != post_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Post title already exists"
                )
            update_dict["title"] = update_data.title
            
            # Generate new slug if title changed
            if update_data.title != post["title"]:
                new_slug = self._generate_slug(update_data.title)
                existing_post_by_slug = await self.post_model.find_post_by_slug(new_slug)
                if existing_post_by_slug and str(existing_post_by_slug["_id"]) != post_id:
                    new_slug = f"{new_slug}-{int(datetime.now().timestamp())}"
                update_dict["slug"] = new_slug
        
        if update_data.content is not None:
            update_dict["content"] = update_data.content
        if update_data.category is not None:
            update_dict["category"] = update_data.category
        if update_data.image is not None:
            update_dict["image"] = update_data.image
        
        # Update post
        if update_dict:  # Only update if there are changes
            success = await self.post_model.update_post(post_id, update_dict)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update post"
                )
        
        # Get updated post
        updated_post = await self.post_model.find_post_by_id(post_id)
        return PostResponse(
            id=str(updated_post["_id"]),
            userId=updated_post["userId"],
            title=updated_post["title"],
            content=updated_post["content"],
            image=updated_post.get("image"),
            category=updated_post.get("category", "uncategorized"),
            slug=updated_post["slug"],
            createdAt=updated_post.get("createdAt"),
            updatedAt=updated_post.get("updatedAt")
        )

# Create controller instance
post_controller = PostController()