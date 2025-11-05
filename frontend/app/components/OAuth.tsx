// components/OAuth.tsx - FIXED VERSION
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
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      {/* ✅ FIXED BUTTON - Remove isProcessing prop */}
      <Button 
        type='button' 
        color="purple" 
        outline 
        onClick={handleGoogleClick}
        disabled={loading}
        className="w-full transition-all duration-200"
      >
        {loading ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600 mr-2"></div>
            Connecting to Google...
          </>
        ) : (
          <>
            <AiFillGoogleCircle className='w-6 h-6 mr-2'/>
            Continue with Google
          </>
        )}
      </Button>
      
      {error && (
        <p className="mt-2 text-sm text-red-600 dark:text-red-400 text-center">
          {error}
        </p>
      )}
    </div>
  );
}