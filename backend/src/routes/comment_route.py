# routes/comment_route.py
from fastapi import APIRouter, Depends, Query
from ..controllers.comment_controller import comment_controller
from ..schemas.comment_schema import CommentCreate, CommentUpdate, CommentResponse, CommentsResponse
from ..utils.auth_dependency import get_current_user

router = APIRouter()

@router.post("/create", response_model=CommentResponse)
async def create_comment(
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new comment"""
    return await comment_controller.create_comment(comment_data, current_user)

@router.get("/getPostComments/{post_id}", response_model=list[CommentResponse])
async def get_post_comments(post_id: str):
    """Get comments for a specific post"""
    return await comment_controller.get_post_comments(post_id)

@router.put("/likeComment/{comment_id}", response_model=CommentResponse)
async def like_comment(
    comment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Like or unlike a comment"""
    return await comment_controller.like_comment(comment_id, current_user)

@router.put("/editComment/{comment_id}", response_model=CommentResponse)
async def edit_comment(
    comment_id: str,
    update_data: CommentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Edit a comment"""
    return await comment_controller.edit_comment(comment_id, update_data, current_user)

@router.delete("/deleteComment/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a comment"""
    return await comment_controller.delete_comment(comment_id, current_user)

@router.get("/getcomments", response_model=CommentsResponse)
async def get_comments(
    current_user: dict = Depends(get_current_user),
    startIndex: int = Query(0, ge=0),
    limit: int = Query(9, ge=1, le=100),
    sort: str = Query("desc", regex="^(asc|desc)$")
):
    """Get all comments (admin only)"""
    return await comment_controller.get_comments(current_user, startIndex, limit, sort)