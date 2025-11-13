# routes/post_route.py (CSRF Compatible Version)
from fastapi import APIRouter, Depends, Query, HTTPException
from bson import ObjectId
from ..controllers.post_controller import post_controller
from ..schemas.post_schema import PostCreate, PostUpdate, PostResponse, PostsResponse
from ..utils.auth_dependency import get_current_user
from ..utils.csrf_dependency import verify_csrf_token  # ✅ CSRF import

router = APIRouter()

@router.post("/create", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    current_user: dict = Depends(verify_csrf_token)  # ✅ CSRF protection
):
    """Create a new post (Admin only)"""
    return await post_controller.create_post(post_data, current_user)

@router.get("/getposts", response_model=PostsResponse)
async def get_posts(
    userId: str = Query(None),
    category: str = Query(None),
    slug: str = Query(None),
    postId: str = Query(None),
    searchTerm: str = Query(None),
    startIndex: int = Query(0, ge=0),
    limit: int = Query(9, ge=1, le=100),
    order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: dict = Depends(get_current_user)  # ✅ Authentication but no CSRF for GET
):
    """Get posts with filtering and pagination"""
    return await post_controller.get_posts(
        userId=userId,
        category=category,
        slug=slug,
        postId=postId,
        searchTerm=searchTerm,
        startIndex=startIndex,
        limit=limit,
        order=order,
        current_user=current_user  # ✅ Pass current_user to controller
    )

@router.get("/{post_id}", response_model=PostResponse)
async def get_single_post(
    post_id: str,
    current_user: dict = Depends(get_current_user)  # ✅ Optional authentication
):
    """Get single post by ID"""
    posts_response = await post_controller.get_posts(
        postId=post_id, 
        limit=1,
        current_user=current_user
    )
    if not posts_response.posts:
        raise HTTPException(status_code=404, detail="Post not found")
    return posts_response.posts[0]

@router.delete("/deletepost/{post_id}/{user_id}")
async def delete_post(
    post_id: str,
    user_id: str,
    current_user: dict = Depends(verify_csrf_token)  # ✅ CSRF protection
):
    """Delete a post"""
    return await post_controller.delete_post(post_id, user_id, current_user)

@router.put("/updatepost/{post_id}/{user_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    user_id: str,
    update_data: PostUpdate,
    current_user: dict = Depends(verify_csrf_token)  # ✅ CSRF protection
):
    """Update a post"""
    return await post_controller.update_post(post_id, user_id, update_data, current_user)

# ✅ NEW: Public endpoints (no authentication required)
@router.get("/public/getposts", response_model=PostsResponse)
async def get_public_posts(
    userId: str = Query(None),
    category: str = Query(None),
    slug: str = Query(None),
    postId: str = Query(None),
    searchTerm: str = Query(None),
    startIndex: int = Query(0, ge=0),
    limit: int = Query(9, ge=1, le=100),
    order: str = Query("desc", regex="^(asc|desc)$")
):
    """Get posts publicly (no authentication required)"""
    return await post_controller.get_posts(
        userId=userId,
        category=category,
        slug=slug,
        postId=postId,
        searchTerm=searchTerm,
        startIndex=startIndex,
        limit=limit,
        order=order,
        current_user=None  # ✅ No user authentication for public access
    )

@router.get("/public/{post_id}", response_model=PostResponse)
async def get_public_single_post(post_id: str):
    """Get single post publicly by ID"""
    posts_response = await post_controller.get_posts(
        postId=post_id, 
        limit=1,
        current_user=None  # ✅ Public access
    )
    if not posts_response.posts:
        raise HTTPException(status_code=404, detail="Post not found")
    return posts_response.posts[0]