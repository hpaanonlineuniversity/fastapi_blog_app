# schemas/post_schema.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    title: str
    content: str
    image: Optional[str] = None
    category: Optional[str] = "uncategorized"

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None
    category: Optional[str] = None

class PostResponse(BaseModel):
    id: str
    userId: str
    title: str
    content: str
    image: Optional[str]
    category: Optional[str]
    slug: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class PostsResponse(BaseModel):
    posts: list[PostResponse]
    totalPosts: int
    lastMonthPosts: int