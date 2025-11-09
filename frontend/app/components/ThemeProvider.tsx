// components/ThemeProvider.tsx
'use client';

import { useSelector } from 'react-redux';
import { RootState } from '../types/redux';
import { useEffect } from 'react';

interface ThemeProviderProps {
  children: React.ReactNode;
}

export default function ThemeProvider({ children }: ThemeProviderProps) {
  const { theme } = useSelector((state: RootState) => state.theme);

  useEffect(() => {
    const html = document.documentElement;
    
    // ရှိပြီးသား theme classes တွေဖျက်
    html.classList.remove('light', 'dark');
    
    // အသစ်ထည့်
    html.classList.add(theme);
    
    console.log('Theme changed to:', theme); // Debugging အတွက်
  }, [theme]);

  return (
    <div className={theme}>
      <div className='bg-white text-gray-700 dark:text-gray-200 dark:bg-[rgb(16,23,42)] min-h-screen'>
        {children}
      </div>
    </div>
  );
}