// app/callback/page.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useDispatch } from 'react-redux';
import { supabase } from '../../lib/supabase';
import { signInSuccess } from '../../redux/user/userSlice';
import { apiInterceptor } from '../../utils/apiInterceptor';

interface UserSession {
  user: {
    email: string;
    user_metadata: {
      user_name?: string;
      name?: string;
      full_name?: string;
      avatar_url?: string;
    };
  };
}

interface ApiUser {
  _id: string;
  username: string;
  email: string;
  profilePicture: string;
  isAdmin: boolean;
}

interface ApiResponse {
  user: ApiUser;
}

export default function CallbackPage() {
  const router = useRouter();
  const dispatch = useDispatch();

  useEffect(() => {
    const getUser = async () => {
      try {
        // Check session
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error('Session error:', error);
          router.push('/sign-in');
          return;
        }

        if (session) {
          const user = (session as unknown as UserSession).user;
          
          // User information
          const userData = {
            email: user.email,
            name: user.user_metadata.user_name || 
                  user.user_metadata.name || 
                  user.user_metadata.full_name ||
                  user.email?.split('@')[0] || 'User',
            photo: user.user_metadata.avatar_url
          };        
          
          console.log('User Info:', userData);

          // Send to backend
          const res = await apiInterceptor.request('/api/auth/google', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
              name: userData.name,
              email: userData.email,
              photo: userData.photo,
            }),
          });
          
          const data: ApiResponse = await res.json();

          console.log("apiResponse",data);
          
          const githubuserData = {
            _id: data.user._id,
            username: data.user.username,
            email: data.user.email,
            profilePicture: data.user.profilePicture,
            isAdmin: data.user.isAdmin,
          };

          dispatch(signInSuccess(githubuserData));
          router.push('/');
        } else {
          console.log('No session found');
          router.push('/sign-in');
        }
      } catch (error) {
        console.error('Error in callback:', error);
        router.push('/sign-in');
      }
    };

    getUser();
  }, [router, dispatch]);

  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
        <p className="mt-4 text-gray-600">Processing authentication...</p>
      </div>
    </div>
  );
}