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
  csrfToken: string | null; // ✅ CSRF token ကို state ထဲမှာသိမ်းမယ်
}

const initialState: UserState = {
  currentUser: null,
  loading: false,
  error: false,
  csrfToken: null, // ✅ initial state
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
      state.csrfToken = action.payload.csrfToken || null; // ✅ CSRF token သိမ်း
      state.loading = false;
      state.error = false;
    },
    signInFailure: (state, action: PayloadAction<string | ApiError>) => {
      state.loading = false;
      state.error = action.payload;
      state.csrfToken = null; // ✅ Error ဖြစ်ရင် clear
    },
    setCsrfToken: (state, action: PayloadAction<string>) => {
      state.csrfToken = action.payload; // ✅ CSRF token သပ်သပ်ထည့်လို့ရ
    },
    clearCsrfToken: (state) => {
      state.csrfToken = null; // ✅ CSRF token ဖျက်လို့ရ
    },
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
      state.csrfToken = null; // ✅ User delete လုပ်ရင် CSRF token ပါဖျက်
      state.loading = false;
      state.error = false;
    },
    deleteUserFailure: (state, action: PayloadAction<string | ApiError>) => {
      state.loading = false;
      state.error = action.payload;
    },
    signOut: (state) => {
      state.currentUser = null;
      state.csrfToken = null; // ✅ Logout လုပ်ရင် CSRF token ပါဖျက်
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
  setCsrfToken,        // ✅ Export new actions
  clearCsrfToken,      // ✅ Export new actions
} = userSlice.actions;

export default userSlice.reducer;