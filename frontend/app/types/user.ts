export interface User {
  id: string;
  username: string;
  email: string;
  profilePicture?: string;
  isAdmin: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export interface UserState {
  currentUser: User | null;
  loading: boolean;
  error: string | null;
}

export interface UserState {
  currentUser: User | null;
  loading: boolean;
  error: string | null;
}

export interface UpdateUserPayload {
  id: string;
  username?: string;
  email?: string;
  password?: string;
  profilePicture?: string;
}

export interface ApiError {
  message: string;
  success?: boolean;
}