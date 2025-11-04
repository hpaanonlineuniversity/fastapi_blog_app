# schemas/comment_schema.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CommentCreate(BaseModel):
    content: str
    postId: str
    userId: str

class CommentUpdate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: str
    content: str
    postId: str
    userId: str
    likes: List[str] = []
    numberOfLikes: int = 0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class CommentsResponse(BaseModel):
    comments: List[CommentResponse]
    totalComments: int
    lastMonthComments: int