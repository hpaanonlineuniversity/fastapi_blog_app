import { User } from './user';


export interface ThemeState {
  theme: 'light' | 'dark';
}


export interface UserState {
  currentUser: User | null;
  loading: boolean;
  error: string | null;
}

export interface RootState {
  user: {
    currentUser: User | null;
    loading: boolean;
    error: string | null;
  };
  theme: ThemeState;
}

