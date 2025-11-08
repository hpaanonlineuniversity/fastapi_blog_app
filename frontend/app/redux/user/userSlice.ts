// redux/user/userSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface User {
  id?: string;
  username: string;
  email: string;
  profilePicture?: string;
}

interface ApiError {
  message?: string;
  success?: boolean;
  statusCode?: number;
  error?: string;
}

interface UserState {
  currentUser: User | null;
  loading: boolean;
  error: string | ApiError | false;  // ✅ string သို့မဟုတ် ApiError လက်ခံမယ်
}

const initialState: UserState = {
  currentUser: null,
  loading: false,
  error: false,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = false;
    },
    signInStart: (state) => {
      state.loading = true;
    },
    signInSuccess: (state, action: PayloadAction<User>) => {
      state.currentUser = action.payload;
      state.loading = false;
      state.error = false;
    },
    signInFailure: (state, action: PayloadAction<string | ApiError>) => {  // ✅ ဒီမှာလည်း ပြင်ပါ
      state.loading = false;
      state.error = action.payload;
    },
    updateUserStart: (state) => {
      state.loading = true;
    },
    updateUserSuccess: (state, action: PayloadAction<User>) => {
      state.currentUser = action.payload;
      state.loading = false;
      state.error = false;
    },
    updateUserFailure: (state, action: PayloadAction<string | ApiError>) => {  // ✅ string | ApiError လက်ခံမယ်
      state.loading = false;
      state.error = action.payload;
    },
    deleteUserStart: (state) => {
      state.loading = true;
    },
    deleteUserSuccess: (state) => {
      state.currentUser = null;
      state.loading = false;
      state.error = false;
    },
    deleteUserFailure: (state, action: PayloadAction<string | ApiError>) => {  // ✅ ဒီမှာလည်း ပြင်ပါ
      state.loading = false;
      state.error = action.payload;
    },
    signOut: (state) => {
      state.currentUser = null;
      state.loading = false;
      state.error = false;
    },
  },
});

export const {
  signInStart,
  signInSuccess,
  signInFailure,
  clearError,
  updateUserFailure,
  updateUserSuccess,
  signOut,
  updateUserStart,
  deleteUserFailure,
  deleteUserStart,
  deleteUserSuccess,
} = userSlice.actions;

export default userSlice.reducer;