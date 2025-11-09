export interface Comment {
  id: string;
  content: string;
  numberOfLikes: number;
  postId: string;
  userId: string;
  createdAt: string;
  updatedAt?: string;
}

export interface CommentsResponse {
  comments: Comment[];
  hasMore?: boolean;
}