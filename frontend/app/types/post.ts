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