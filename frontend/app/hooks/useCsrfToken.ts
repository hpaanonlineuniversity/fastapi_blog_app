// hooks/useCsrfToken.ts
import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from './redux';
import { checkCsrfTokenExpiry } from '../redux/user/userSlice';

export const useCsrfToken = () => {
  const dispatch = useAppDispatch();
  const { csrfToken, csrfTokenExpiry } = useAppSelector((state) => state.user);

  // Check token expiry on component mount and regularly
  useEffect(() => {
    // Check immediately
    dispatch(checkCsrfTokenExpiry());

    // Set up interval to check every minute
    const interval = setInterval(() => {
      dispatch(checkCsrfTokenExpiry());
    }, 60000); // Check every minute

    return () => clearInterval(interval);
  }, [dispatch]);

  // Helper function to check if token is valid
  const isTokenValid = (): boolean => {
    if (!csrfToken || !csrfTokenExpiry) return false;
    return Date.now() < csrfTokenExpiry;
  };

  // Helper function to get token if valid
  const getValidToken = (): string | null => {
    return isTokenValid() ? csrfToken : null;
  };

  // Helper function to get time remaining in minutes
  const getTimeRemaining = (): number => {
    if (!csrfTokenExpiry) return 0;
    const remaining = csrfTokenExpiry - Date.now();
    return Math.max(0, Math.ceil(remaining / 60000)); // Convert to minutes
  };

  return {
    csrfToken,
    isTokenValid,
    getValidToken,
    getTimeRemaining,
    csrfTokenExpiry
  };
};