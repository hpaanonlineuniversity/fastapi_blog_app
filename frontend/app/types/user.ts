export interface User {
  _id: string;
  username: string;
  email: string;
  profilePicture?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface UserState {
  currentUser: User | null;
  loading: boolean;
  error: string | null;
}

export interface UpdateUserPayload {
  username?: string;
  email?: string;
  password?: string;
  profilePicture?: string;
}

export interface ApiError {
  message: string;
  success?: boolean;
}