// components/OAuth.tsx (Enhanced version)
'use client';

import { Button } from 'flowbite-react';
import { AiFillGoogleCircle } from 'react-icons/ai';
import { useState } from 'react';
import { supabase } from '../lib/supabase';

export default function OAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGoogleClick = async () => {
    try {
      setLoading(true);
      setError(null);

      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          }
        }
      });

      if (error) {
        throw new Error(error.message);
      }
    } catch (error) {
      console.error('Google OAuth error:', error);
      setError((error as Error).message || 'Failed to sign in with Google');
      // You can replace this with a toast notification
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      <Button 
        type='button' 
        color="purple" 
        outline 
        onClick={handleGoogleClick}
        disabled={loading}
        className="w-full transition-all duration-200"
        isProcessing={loading}
      >
        {!loading && <AiFillGoogleCircle className='w-6 h-6 mr-2'/>}
        {loading ? 'Connecting to Google...' : 'Continue with Google'}
      </Button>
      
      {error && (
        <p className="mt-2 text-sm text-red-600 dark:text-red-400 text-center">
          {error}
        </p>
      )}
    </div>
  );
}