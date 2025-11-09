'use client';

import { useSelector } from 'react-redux';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { RootState } from '../types/redux';

interface PrivateRouteProps {
  children: React.ReactNode;
}

export default function PrivateRoute({ children }: PrivateRouteProps) {
  const { currentUser } = useSelector((state: RootState) => state.user);
  const router = useRouter();

  useEffect(() => {
    if (!currentUser) {
      router.push('/sign-in');
    }
  }, [currentUser, router]);

  if (!currentUser) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return <>{children}</>;
}