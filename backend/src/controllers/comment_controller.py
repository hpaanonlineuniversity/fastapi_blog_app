# controllers/comment_controller.py (CSRF Compatible Version)
from fastapi import HTTPException, status
from ..models.comment_model import CommentModel
from ..schemas.comment_schema import CommentCreate, CommentUpdate, CommentResponse, CommentsResponse
from datetime import datetime, timedelta

class CommentController:
    def __init__(self):
        self.comment_model = CommentModel()

    async def create_comment(self, comment_data: CommentCreate, current_user: dict):
        """Create a new comment"""
        # Validate current_user exists (CSRF protection ensures this)
        if not current_user or "id" not in current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Check if user is creating comment for themselves
        if comment_data.userId != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to create this comment"
            )
        
        # Validate required fields
        if not comment_data.content or not comment_data.postId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content and postId are required"
            )
        
        # Create comment data
        comment_dict = {
            "content": comment_data.content,
            "postId": comment_data.postId,
            "userId": comment_data.userId,
            "likes": [],
            "numberOfLikes": 0,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        # Save comment
        comment_id = await self.comment_model.create_comment(comment_dict)
        
        # Get the created comment
        new_comment = await self.comment_model.find_comment_by_id(comment_id)
        if not new_comment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment"
            )
        
        return CommentResponse(
            id=str(new_comment["_id"]),
            content=new_comment["content"],
            postId=new_comment["postId"],
            userId=new_comment["userId"],
            likes=new_comment.get("likes", []),
            numberOfLikes=new_comment.get("numberOfLikes", 0),
            createdAt=new_comment.get("createdAt"),
            updatedAt=new_comment.get("updatedAt")
        )

    async def get_post_comments(self, post_id: str, current_user: dict = None):
        """Get comments for a specific post"""
        if not post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post ID is required"
            )
        
        comments = await self.comment_model.get_comments_by_post_id(post_id, sort_direction=-1)
        
        comments_response = []
        for comment in comments:
            comments_response.append(CommentResponse(
                id=str(comment["_id"]),
                content=comment["content"],
                postId=comment["postId"],
                userId=comment["userId"],
                likes=comment.get("likes", []),
                numberOfLikes=comment.get("numberOfLikes", 0),
                createdAt=comment.get("createdAt"),
                updatedAt=comment.get("updatedAt")
            ))
        
        return comments_response

    async def like_comment(self, comment_id: str, current_user: dict):
        """Like or unlike a comment"""
        # Validate current_user exists (CSRF protection ensures this)
        if not current_user or "id" not in current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        comment = await self.comment_model.find_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        user_id = current_user["id"]
        likes = comment.get("likes", [])
        
        # Check if user already liked the comment
        if user_id in likes:
            # Unlike: remove user from likes
            likes.remove(user_id)
            number_of_likes = comment.get("numberOfLikes", 0) - 1
        else:
            # Like: add user to likes
            likes.append(user_id)
            number_of_likes = comment.get("numberOfLikes", 0) + 1
        
        # Update comment
        success = await self.comment_model.update_comment(comment_id, {
            "likes": likes,
            "numberOfLikes": number_of_likes,
            "updatedAt": datetime.now()
        })
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update comment"
            )
        
        # Get updated comment
        updated_comment = await self.comment_model.find_comment_by_id(comment_id)
        return CommentResponse(
            id=str(updated_comment["_id"]),
            content=updated_comment["content"],
            postId=updated_comment["postId"],
            userId=updated_comment["userId"],
            likes=updated_comment.get("likes", []),
            numberOfLikes=updated_comment.get("numberOfLikes", 0),
            createdAt=updated_comment.get("createdAt"),
            updatedAt=updated_comment.get("updatedAt")
        )

    async def edit_comment(self, comment_id: str, update_data: CommentUpdate, current_user: dict):
        """Edit a comment"""
        # Validate current_user exists (CSRF protection ensures this)
        if not current_user or "id" not in current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        comment = await self.comment_model.find_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Check permissions
        if comment["userId"] != current_user["id"] and not current_user.get("isAdmin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to edit this comment"
            )
        
        # Validate content
        if not update_data.content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment content cannot be empty"
            )
        
        # Update comment content
        success = await self.comment_model.update_comment(comment_id, {
            "content": update_data.content,
            "updatedAt": datetime.now()
        })
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update comment"
            )
        
        # Get updated comment
        updated_comment = await self.comment_model.find_comment_by_id(comment_id)
        return CommentResponse(
            id=str(updated_comment["_id"]),
            content=updated_comment["content"],
            postId=updated_comment["postId"],
            userId=updated_comment["userId"],
            likes=updated_comment.get("likes", []),
            numberOfLikes=updated_comment.get("numberOfLikes", 0),
            createdAt=updated_comment.get("createdAt"),
            updatedAt=updated_comment.get("updatedAt")
        )

    async def delete_comment(self, comment_id: str, current_user: dict):
        """Delete a comment"""
        # Validate current_user exists (CSRF protection ensures this)
        if not current_user or "id" not in current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        comment = await self.comment_model.find_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Check permissions
        if comment["userId"] != current_user["id"] and not current_user.get("isAdmin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to delete this comment"
            )
        
        success = await self.comment_model.delete_comment(comment_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete comment"
            )
        
        return {"message": "Comment has been deleted"}

    async def get_comments(
        self, 
        current_user: dict = None, 
        start_index: int = 0, 
        limit: int = 9, 
        sort: str = "desc"
    ):
        """Get all comments (admin only for full access)"""
        sort_direction = -1 if sort == "desc" else 1
        
        # ✅ If no current_user (public access), apply limitations
        if not current_user:
            # Public access - limit results and apply filters if needed
            limit = min(limit, 50)  # Limit public access to 50 comments
            # You can add additional filters for public access here
        
        # ✅ If user is not admin, restrict access
        elif not current_user.get("isAdmin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to get all comments"
            )
        
        # Get comments
        comments = await self.comment_model.get_all_comments(
            skip=start_index, 
            limit=limit, 
            sort_direction=sort_direction
        )
        
        # Convert to response format
        comments_response = []
        for comment in comments:
            comments_response.append(CommentResponse(
                id=str(comment["_id"]),
                content=comment["content"],
                postId=comment["postId"],
                userId=comment["userId"],
                likes=comment.get("likes", []),
                numberOfLikes=comment.get("numberOfLikes", 0),
                createdAt=comment.get("createdAt"),
                updatedAt=comment.get("updatedAt")
            ))
        
        # Get counts
        total_comments = await self.comment_model.count_comments()
        
        # Last month comments count
        one_month_ago = datetime.now() - timedelta(days=30)
        last_month_comments = await self.comment_model.get_comments_count_since_date(one_month_ago)
        
        return CommentsResponse(
            comments=comments_response,
            totalComments=total_comments,
            lastMonthComments=last_month_comments
        )

# Create controller instance
comment_controller = CommentController()