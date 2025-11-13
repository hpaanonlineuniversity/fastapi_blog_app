# routes/comment_route.py (CSRF Compatible Version)
from fastapi import APIRouter, Depends, Query, HTTPException
from ..controllers.comment_controller import comment_controller
from ..schemas.comment_schema import CommentCreate, CommentUpdate, CommentResponse, CommentsResponse
from ..utils.auth_dependency import get_current_user
from ..utils.csrf_dependency import verify_csrf_token  # ✅ CSRF import

router = APIRouter()

@router.post("/create", response_model=CommentResponse)
async def create_comment(
    comment_data: CommentCreate,
    current_user: dict = Depends(verify_csrf_token)  # ✅ CSRF protection
):
    """Create a new comment"""
    return await comment_controller.create_comment(comment_data, current_user)

@router.get("/getPostComments/{post_id}", response_model=list[CommentResponse])
async def get_post_comments(
    post_id: str,
    current_user: dict = Depends(get_current_user)  # ✅ Optional authentication
):
    """Get comments for a specific post"""
    return await comment_controller.get_post_comments(post_id, current_user)

@router.put("/likeComment/{comment_id}", response_model=CommentResponse)
async def like_comment(
    comment_id: str,
    current_user: dict = Depends(verify_csrf_token)  # ✅ CSRF protection
):
    """Like or unlike a comment"""
    return await comment_controller.like_comment(comment_id, current_user)

@router.put("/editComment/{comment_id}", response_model=CommentResponse)
async def edit_comment(
    comment_id: str,
    update_data: CommentUpdate,
    current_user: dict = Depends(verify_csrf_token)  # ✅ CSRF protection
):
    """Edit a comment"""
    return await comment_controller.edit_comment(comment_id, update_data, current_user)

@router.delete("/deleteComment/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: dict = Depends(verify_csrf_token)  # ✅ CSRF protection
):
    """Delete a comment"""
    return await comment_controller.delete_comment(comment_id, current_user)

@router.get("/getcomments", response_model=CommentsResponse)
async def get_comments(
    current_user: dict = Depends(get_current_user),  # ✅ GET - no CSRF needed
    startIndex: int = Query(0, ge=0),
    limit: int = Query(9, ge=1, le=100),
    sort: str = Query("desc", regex="^(asc|desc)$")
):
    """Get all comments (admin only)"""
    return await comment_controller.get_comments(current_user, startIndex, limit, sort)

# ✅ NEW: Public endpoints for comments
@router.get("/public/getPostComments/{post_id}", response_model=list[CommentResponse])
async def get_public_post_comments(post_id: str):
    """Get comments for a specific post (public access)"""
    return await comment_controller.get_post_comments(post_id, None)  # ✅ No user authentication

@router.get("/public/getcomments", response_model=CommentsResponse)
async def get_public_comments(
    startIndex: int = Query(0, ge=0),
    limit: int = Query(9, ge=1, le=100),
    sort: str = Query("desc", regex="^(asc|desc)$")
):
    """Get all comments publicly (with limitations)"""
    return await comment_controller.get_comments(None, startIndex, limit, sort)  # ✅ Public access