// redux/theme/themeSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ThemeState {
  theme: 'light' | 'dark';
}


// Check if we're in browser and get initial theme from localStorage
const getInitialTheme = (): 'light' | 'dark' => {
  if (typeof window !== 'undefined') {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark';
    return savedTheme || 'light';
  }
  return 'light';
};


const initialState: ThemeState = {
  theme: getInitialTheme(),
};

export const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
      // Save to localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('theme', state.theme);
      }
    },
    setTheme: (state, action) => {
      state.theme = action.payload;
      if (typeof window !== 'undefined') {
        localStorage.setItem('theme', action.payload);
      }
    },
  },
});

export const { setTheme, toggleTheme } = themeSlice.actions;
export default themeSlice.reducer;
