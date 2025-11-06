// app/auth/callback/page.tsx - CORRECTED VERSION
'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useDispatch } from 'react-redux';
import { supabase } from '../../lib/supabase';
import { signInSuccess } from '../../redux/user/userSlice';
import { apiInterceptor } from '@/app/utils/apiInterceptor';

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
  const [status, setStatus] = useState('Initializing authentication...');
  const hasProcessed = useRef(false);

  useEffect(() => {
    // ✅ Prevent the effect from running twice in same session
    if (hasProcessed.current) {
      return;
    }
    hasProcessed.current = true;

    const handleAuthCallback = async () => {
      try {
        setStatus('Processing OAuth response...');

        // Wait for Supabase to process the OAuth callback
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Get the session after OAuth processing
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        
        if (sessionError) {
          console.error('Session error:', sessionError);
          throw new Error(`Authentication failed: ${sessionError.message}`);
        }

        if (!session?.user) {
          // Try alternative method to get session
          const { data: { user }, error: userError } = await supabase.auth.getUser();
          
          if (userError || !user) {
            console.log('No user session found');
            throw new Error('Please try signing in again');
          }
          
          // If we have user but no session, process user data
          await processUserData(user);
          return;
        }

        // Process the session normally
        await processUserData(session.user);

      } catch (error) {
        console.error('Auth callback error:', error);
        setStatus(`Error: ${(error as Error).message}`);
        
        setTimeout(() => {
          router.push('/sign-in');
        }, 3000);
      }
    };

    const processUserData = async (user: any) => {
      try {
        setStatus('Processing user information...');
        
        // Extract user data from GitHub OAuth
        const userData = {
          email: user.email,
          name: user.user_metadata.user_name || 
                user.user_metadata.name || 
                user.user_metadata.full_name ||
                user.user_metadata.preferred_username ||
                user.user_metadata.email?.split('@')[0] ||
                user.email?.split('@')[0] || 'User',
          photo: user.user_metadata.avatar_url || 
                user.user_metadata.picture
        };

        console.log('GitHub User Info:', userData);

        setStatus('Connecting to backend...');

        // ✅ FIXED: Remove sessionStorage check that blocks subsequent logins
        // We only use useRef to prevent duplicate execution in same component mount

        // Send to backend API
        const res = await apiInterceptor.request('/api/auth/github', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: userData.name,
            email: userData.email,
            googlePhotoUrl: userData.photo,
            provider: 'github',
          }),
        });

        if (!res.ok) {
          throw new Error(`Backend error: ${res.status}`);
        }

        const data: ApiResponse = await res.json();
        console.log("Backend API Response:", data);

        setStatus('Setting up your account...');

        // Update Redux store
        const userDataForRedux = {
          _id: data.user._id,
          username: data.user.username,
          email: data.user.email,
          profilePicture: data.user.profilePicture,
          isAdmin: data.user.isAdmin,
        };

        dispatch(signInSuccess(userDataForRedux));
        
        setStatus('Success! Redirecting...');
        
        setTimeout(() => {
          router.push('/');
        }, 1000);

      } catch (error) {
        console.error('Error processing user data:', error);
        throw error;
      }
    };

    handleAuthCallback();
  }, [router, dispatch]);

  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="text-center max-w-md">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-600 font-medium">{status}</p>
        <p className="text-sm text-gray-500 mt-2">
          Please wait while we complete your authentication...
        </p>
      </div>
    </div>
  );
}