// redux/user/userSlice.ts - UPDATED VERSION
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
  error: string | ApiError | false;
  csrfToken: string | null;
  csrfTokenExpiry: number | null; // ✅ Add expiry timestamp
}

const initialState: UserState = {
  currentUser: null,
  loading: false,
  error: false,
  csrfToken: null,
  csrfTokenExpiry: null, // ✅ initial state for expiry
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
    signInSuccess: (state, action: PayloadAction<{user: User, csrfToken?: string}>) => {
      state.currentUser = action.payload.user;
      state.csrfToken = action.payload.csrfToken || null;
      // ✅ Set expiry time (15 minutes from now)
      state.csrfTokenExpiry = action.payload.csrfToken 
        ? Date.now() + (15 * 60 * 1000)
        : null;
      state.loading = false;
      state.error = false;
    },
    signInFailure: (state, action: PayloadAction<string | ApiError>) => {
      state.loading = false;
      state.error = action.payload;
      state.csrfToken = null;
      state.csrfTokenExpiry = null; // ✅ Clear expiry on error
    },
    setCsrfToken: (state, action: PayloadAction<string>) => {
      state.csrfToken = action.payload;
      // ✅ Set expiry time when setting token manually
      state.csrfTokenExpiry = Date.now() + (15 * 60 * 1000);
    },
    clearCsrfToken: (state) => {
      state.csrfToken = null;
      state.csrfTokenExpiry = null;
    },
    // ✅ New action to check and clear expired token
    checkCsrfTokenExpiry: (state) => {
      if (state.csrfToken && state.csrfTokenExpiry && Date.now() > state.csrfTokenExpiry) {
        state.csrfToken = null;
        state.csrfTokenExpiry = null;
        console.log('CSRF token expired and cleared');
      }
    },
    // ... other existing actions
    updateUserStart: (state) => {
      state.loading = true;
    },
    updateUserSuccess: (state, action: PayloadAction<User>) => {
      state.currentUser = action.payload;
      state.loading = false;
      state.error = false;
    },
    updateUserFailure: (state, action: PayloadAction<string | ApiError>) => {
      state.loading = false;
      state.error = action.payload;
    },
    deleteUserStart: (state) => {
      state.loading = true;
    },
    deleteUserSuccess: (state) => {
      state.currentUser = null;
      state.csrfToken = null;
      state.csrfTokenExpiry = null;
      state.loading = false;
      state.error = false;
    },
    deleteUserFailure: (state, action: PayloadAction<string | ApiError>) => {
      state.loading = false;
      state.error = action.payload;
    },
    signOut: (state) => {
      state.currentUser = null;
      state.csrfToken = null;
      state.csrfTokenExpiry = null;
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
  setCsrfToken,
  clearCsrfToken,
  checkCsrfTokenExpiry, // ✅ Export new action
} = userSlice.actions;

export default userSlice.reducer;