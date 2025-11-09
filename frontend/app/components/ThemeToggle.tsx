'use client';

import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../types/redux';
import { toggleTheme } from '../redux/theme/themeSlice'
import { Button } from 'flowbite-react';
import { HiSun, HiMoon } from 'react-icons/hi';

export default function ThemeToggle() {
  const { theme } = useSelector((state: RootState) => state.theme);
  const dispatch = useDispatch();

  return (
    <Button
      color="gray"
      onClick={() => dispatch(toggleTheme())}
      className="bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600"
    >
      {theme === 'light' ? (
        <HiMoon className="w-5 h-5" />
      ) : (
        <HiSun className="w-5 h-5" />
      )}
    </Button>
  );
}