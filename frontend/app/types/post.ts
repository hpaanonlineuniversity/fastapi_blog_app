// types/post.ts
export interface Post {
  id: string;
  title: string;
  content: string;
  image: string;
  category: string;
  slug: string;
  username: string;
  userProfilePicture: string;
  createdAt: string;
  updatedAt?: string;
}

export interface RecentPostsResponse {
  posts: Post[];
}

export interface PostCardProps {
  post?: Post;
  loading?: boolean;
}

export interface PostsResponse {
  posts: Post[];
  totalPosts: number;
  lastMonthPosts: number;
  hasMore?: boolean;
  success?: boolean;
  message?: string;
}

export interface CreatePostResponse {
  success: boolean;
  message?: string;
  slug?: string;
  postId?: string;
  csrfToken?: string;
}