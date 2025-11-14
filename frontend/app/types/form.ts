// Define TypeScript interfaces
export interface FormData {  // used in create post , update post
  title: string;
  category: string;
  content: string;
  image: string;
}

export interface SignInFormData {
  email: string;
  password: string;
}