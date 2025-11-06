// app/sign-in/page.tsx - FIXED VERSION
'use client';

import { Alert, Button, Label, Spinner, TextInput, Card } from 'flowbite-react';
import { useState, FormEvent, ChangeEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import OAuth from '../components/OAuth';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import {
  signInStart,
  signInSuccess,
  signInFailure,
} from '../redux/user/userSlice';
import { apiInterceptor } from '../utils/apiInterceptor';

interface FormData {
  email: string;
  password: string;
}

interface UserData {
  id: string;
  username: string;
  email: string;
  profilePicture: string;
  isAdmin: boolean;
}

interface ApiResponse {
  success: boolean;
  message?: string;
  user?: UserData;
}

export default function SignIn() {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: ''
  });
  const { loading, error: errorMessage } = useAppSelector((state) => state.user);
  const dispatch = useAppDispatch();
  const router = useRouter();

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [id]: value.trim()
    }));
    // Clear error when user starts typing
    if (errorMessage) {
      dispatch(signInFailure(null));
    }
  };

  const validateForm = (): boolean => {
    if (!formData.email.trim()) {
      dispatch(signInFailure('Please enter your email address'));
      return false;
    }
    if (!formData.password.trim()) {
      dispatch(signInFailure('Please enter your password'));
      return false;
    }
    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      dispatch(signInFailure('Please enter a valid email address'));
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      dispatch(signInStart());
      
      const res = await apiInterceptor.request('/api/auth/signin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      
      const data: ApiResponse = await res.json();
      console.log('SignIn Response:', data);

      if (!res.ok || data.success === false) {
        throw new Error(data.message || 'Sign in failed');
      }

      if (data.user) {
        const userData: UserData = {
          id: data.user.id,
          username: data.user.username,
          email: data.user.email,
          profilePicture: data.user.profilePicture,
          isAdmin: data.user.isAdmin,
        };
        
        dispatch(signInSuccess(userData));
        router.push('/');
      }
    } catch (error) {
      console.error('SignIn error:', error);
      dispatch(signInFailure(
        (error as Error).message || 'Sign in failed. Please try again.'
      ));
    }
  };

  return (
    <div className='min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4'>
      <div className='flex justify-center items-center'>
        <div className='max-w-md w-full'>
          {/* Header Card */}
          <Card className='mb-8 text-center'>
            <div className='flex justify-center mb-4'>
              <Link href='/' className='flex items-center gap-2'>
                <span className='px-3 py-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-lg text-white text-2xl font-bold'>
                  Hpa-an's
                </span>
                <span className='text-xl font-semibold dark:text-white'>
                  Blog
                </span>
              </Link>
            </div>
            <a 
              href='https://github.com/hpaanonlineuniversity'
              target='_blank'
              rel='noopener noreferrer'
              className='inline-block mt-2 text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 hover:underline transition-colors duration-200'
            >
              Join our community on GitHub →
            </a>
          </Card>

          {/* Sign In Form Card */}
          <Card>
            <div className='text-center mb-6'>
              <h2 className='text-2xl font-bold text-gray-900 dark:text-white'>
                Welcome Back
              </h2>
              <p className='text-gray-600 dark:text-gray-400 mt-2'>
                Sign in to your account
              </p>
            </div>

            <form className='flex flex-col gap-4' onSubmit={handleSubmit}>
              <div className='space-y-2'>
                <Label htmlFor='email' value='Email Address' />
                <TextInput
                  type='email'
                  placeholder='name@company.com'
                  id='email'
                  value={formData.email}
                  onChange={handleChange}
                  required
                  shadow
                  disabled={loading}
                />
              </div>
              
              <div className='space-y-2'>
                <div className='flex justify-between items-center'>
                  <Label htmlFor='password' value='Password' />
                  <Link 
                    href='/forgot-password'
                    className='text-sm text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 hover:underline transition-colors duration-200'
                  >
                    Forgot password?
                  </Link>
                </div>
                <TextInput
                  type='password'
                  placeholder='Enter your password'
                  id='password'
                  value={formData.password}
                  onChange={handleChange}
                  required
                  shadow
                  disabled={loading}
                />
              </div>

              {/* ✅ FIXED BUTTON - Remove isProcessing prop */}
              <Button
                color="purple"
                type='submit'
                disabled={loading}
                className='w-full mt-2 transition-all duration-200 hover:shadow-lg'
                size='lg'
              >
                {loading ? (
                  <>
                    <Spinner size='sm' />
                    <span className='pl-3'>Signing In...</span>
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>

            {/* Divider */}
            <div className='flex items-center my-6'>
              <div className='flex-1 border-t border-gray-300 dark:border-gray-600'></div>
              <span className='px-3 text-gray-500 dark:text-gray-400 text-sm'>Or continue with</span>
              <div className='flex-1 border-t border-gray-300 dark:border-gray-600'></div>
            </div>

            {/* OAuth Section */}
            <OAuth />

            {/* Sign Up Link */}
            <div className='text-center mt-6 pt-4 border-t border-gray-200 dark:border-gray-700'>
              <span className='text-gray-600 dark:text-gray-400'>
                Don't have an account?{' '}
                <Link 
                  href='/sign-up' 
                  className='text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 font-medium transition-colors duration-200 hover:underline'
                >
                  Sign Up
                </Link>
              </span>
            </div>
          </Card>

          {/* Error Message */}
          {errorMessage && (
            <Alert 
              className='mt-4 animate-fade-in' 
              color='failure'
              onDismiss={() => dispatch(signInFailure(null))}
            >
              <span className='font-medium'>Sign in failed!</span> {errorMessage}
            </Alert>
          )}
        </div>
      </div>
    </div>
  );
}