// app/sign-up/page.tsx (Enhanced version)
'use client';

import { Alert, Button, Label, Spinner, TextInput, Card } from 'flowbite-react';
import { useState, FormEvent, ChangeEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import OAuth from '../components/OAuth';

interface FormData {
  username: string;
  email: string;
  password: string;
}

interface ApiResponse {
  success: boolean;
  message?: string;
  user?: any;
}

export default function SignUp() {
  const [formData, setFormData] = useState<FormData>({
    username: '',
    email: '',
    password: ''
  });
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [id]: value.trim()
    }));
    // Clear error when user starts typing
    if (errorMessage) {
      setErrorMessage(null);
    }
  };

  const validateForm = (): boolean => {
    if (!formData.username.trim()) {
      setErrorMessage('Please enter a username');
      return false;
    }
    if (!formData.email.trim()) {
      setErrorMessage('Please enter an email address');
      return false;
    }
    if (!formData.password.trim()) {
      setErrorMessage('Please enter a password');
      return false;
    }
    if (formData.password.length < 6) {
      setErrorMessage('Password must be at least 6 characters long');
      return false;
    }
    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      setErrorMessage('Please enter a valid email address');
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
      setLoading(true);
      setErrorMessage(null);
      
      const res = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData),
      });
      
      const data: ApiResponse = await res.json();
      
      if (!res.ok || data.success === false) {
        throw new Error(data.message || 'Something went wrong');
      }
      
      // Success - redirect to sign in
      router.push('/sign-in');
      
    } catch (error) {
      console.error('Signup error:', error);
      setErrorMessage(
        (error as Error).message || 'An error occurred during sign up'
      );
    } finally {
      setLoading(false);
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
              className='text-purple-600 hover:text-purple-700 hover:underline transition-colors duration-200'
              target='_blank'
              rel='noopener noreferrer'
            >
              Join our community on GitHub
            </a>
          </Card>

          {/* Sign Up Form Card */}
          <Card>
            <div className='text-center mb-6'>
              <h2 className='text-2xl font-bold text-gray-900 dark:text-white'>
                Create Account
              </h2>
              <p className='text-gray-600 dark:text-gray-400 mt-2'>
                Sign up to get started with our blog
              </p>
            </div>

            <form className='flex flex-col gap-4' onSubmit={handleSubmit}>
              <div className='space-y-2'>
                <Label htmlFor='username' value='Username' />
                <TextInput
                  type='text'
                  placeholder='Enter your username'
                  id='username'
                  value={formData.username}
                  onChange={handleChange}
                  required
                  shadow
                  disabled={loading}
                />
              </div>
              
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
                <Label htmlFor='password' value='Password' />
                <TextInput
                  type='password'
                  placeholder='Create a password (min. 6 characters)'
                  id='password'
                  value={formData.password}
                  onChange={handleChange}
                  required
                  shadow
                  disabled={loading}
                  minLength={6}
                />
              </div>

              <Button
                gradientDuoTone="purpleToPink"
                type='submit'
                disabled={loading}
                className='w-full mt-4 transition-all duration-200'
                size='lg'
                isProcessing={loading}
              >
                {loading ? 'Creating Account...' : 'Sign Up'}
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

            {/* Sign In Link */}
            <div className='text-center mt-6 pt-4 border-t border-gray-200 dark:border-gray-700'>
              <span className='text-gray-600 dark:text-gray-400'>
                Already have an account?{' '}
                <Link 
                  href='/sign-in' 
                  className='text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 font-medium transition-colors duration-200'
                >
                  Sign In
                </Link>
              </span>
            </div>
          </Card>

          {/* Error Message */}
          {errorMessage && (
            <Alert 
              className='mt-4 animate-fade-in' 
              color='failure'
              onDismiss={() => setErrorMessage(null)}
            >
              <span className='font-medium'>Error!</span> {errorMessage}
            </Alert>
          )}
        </div>
      </div>
    </div>
  );
}