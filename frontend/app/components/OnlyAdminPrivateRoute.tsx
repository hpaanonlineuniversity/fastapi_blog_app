'use client';

import { useSelector } from 'react-redux';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { RootState } from '../types/redux';

interface OnlyAdminPrivateRouteProps {
  children: React.ReactNode;
}

export default function OnlyAdminPrivateRoute({ children }: OnlyAdminPrivateRouteProps) {
  const { currentUser } = useSelector((state: RootState) => state.user);
  const router = useRouter();

  useEffect(() => {
    if (!currentUser) {
      router.push('/sign-in');
    } else if (!currentUser.isAdmin) {
      router.push('/');
    }
  }, [currentUser, router]);

  if (!currentUser || !currentUser.isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500"></div>
      </div>
    );
  }

  return <>{children}</>;
}