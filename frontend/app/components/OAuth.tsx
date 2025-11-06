// components/OAuth.tsx - FIXED VERSION
'use client';

import { Button } from 'flowbite-react';
import { AiFillGithub } from 'react-icons/ai';
import { useState } from 'react';
import { supabase } from '../lib/supabase';

export default function OAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGithubClick = async () => {
    try {
      setLoading(true);
      setError(null);

      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'github',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          // ❌ Remove Google-specific parameters for GitHub
          // ✅ GitHub doesn't need access_type or prompt
        }
      });

      if (error) {
        throw new Error(error.message);
      }

      // OAuth flow will redirect to GitHub and back to callback
      
    } catch (error) {
      console.error('GitHub OAuth error:', error);
      setError((error as Error).message || 'Failed to sign in with GitHub');
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
        onClick={handleGithubClick}
        disabled={loading}
        className="w-full transition-all duration-200"
      >
        {loading ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600 mr-2"></div>
            Redirecting to GitHub...
          </>
        ) : (
          <>
            <AiFillGithub className='w-6 h-6 mr-2'/>
            Continue with GitHub
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