// app/sign-up/page.tsx - FIXED VERSION
'use client';

import { Alert, Button, Label, Spinner, TextInput, Card, Progress, Tooltip } from 'flowbite-react';
import { useState, FormEvent, ChangeEvent, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import OAuth from '../components/OAuth';
import { apiInterceptor } from '../utils/apiInterceptor';
import { HiCheck, HiX, HiInformationCircle, HiExclamation } from 'react-icons/hi';
import { debounce } from 'lodash';

interface FormData {
  username?: string;
  email?: string;
  password?: string;
}

interface PasswordValidation {
  hasMinLength: boolean;
  hasUppercase: boolean;
  hasLowercase: boolean;
  hasNumber: boolean;
  hasSpecialChar: boolean;
  score: number;
  strength: 'weak' | 'medium' | 'strong';
}

interface AvailabilityCheck {
  email: { available: boolean; checking: boolean; message?: string };
  username: { available: boolean; checking: boolean; message?: string };
}

export default function SignUp() {
  const [formData, setFormData] = useState<FormData>({});
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [passwordValidation, setPasswordValidation] = useState<PasswordValidation>({
    hasMinLength: false,
    hasUppercase: false,
    hasLowercase: false,
    hasNumber: false,
    hasSpecialChar: false,
    score: 0,
    strength: 'weak'
  });
  const [showPassword, setShowPassword] = useState(false);
  const [availability, setAvailability] = useState<AvailabilityCheck>({
    email: { available: false, checking: false },
    username: { available: false, checking: false }
  });
  const router = useRouter();

  // Debounced availability check functions
  const checkEmailAvailability = useCallback(
    debounce(async (email: string) => {
      if (!email || email.length < 3) {
        setAvailability(prev => ({
          ...prev,
          email: { available: false, checking: false, message: 'Enter a valid email' }
        }));
        return;
      }

      // Basic email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        setAvailability(prev => ({
          ...prev,
          email: { available: false, checking: false, message: 'Please enter a valid email address' }
        }));
        return;
      }

      setAvailability(prev => ({
        ...prev,
        email: { available: false, checking: true, message: 'Checking email availability...' }
      }));

      try {
        // Use the new dedicated endpoint
        const res = await apiInterceptor.request(`/api/auth/check-email/${encodeURIComponent(email)}`, {
          method: 'GET',
          credentials: 'include'
        });
        
        if (res.ok) {
          const data = await res.json();
          setAvailability(prev => ({
            ...prev,
            email: { 
              available: data.available, 
              checking: false, 
              message: data.message
            }
          }));
        } else {
          throw new Error('Failed to check email availability');
        }
      } catch (error) {
        // If endpoint doesn't exist yet, we'll do basic validation only
        console.log('Email check endpoint not available, using basic validation');
        setAvailability(prev => ({
          ...prev,
          email: { available: true, checking: false, message: 'Email format is valid' }
        }));
      }
    }, 800), // Increased debounce time to reduce API calls
    []
  );

  const checkUsernameAvailability = useCallback(
    debounce(async (username: string) => {
      if (!username || username.length < 3) {
        setAvailability(prev => ({
          ...prev,
          username: { available: false, checking: false, message: 'Username is too short' }
        }));
        return;
      }

      // Username validation
      if (username.length < 6 || username.length > 40) {
        setAvailability(prev => ({
          ...prev,
          username: { available: false, checking: false, message: 'Username must be 6-40 characters' }
        }));
        return;
      }

      if (username !== username.toLowerCase()) {
        setAvailability(prev => ({
          ...prev,
          username: { available: false, checking: false, message: 'Username must be lowercase' }
        }));
        return;
      }

      if (!/^[a-z0-9]+$/.test(username)) {
        setAvailability(prev => ({
          ...prev,
          username: { available: false, checking: false, message: 'Username can only contain letters and numbers' }
        }));
        return;
      }

      setAvailability(prev => ({
        ...prev,
        username: { available: false, checking: true, message: 'Checking username availability...' }
      }));

      try {
        // Use the new dedicated endpoint
        const res = await apiInterceptor.request(`/api/auth/check-username/${encodeURIComponent(username)}`, {
          method: 'GET',
          credentials: 'include'
        });
        
        if (res.ok) {
          const data = await res.json();
          setAvailability(prev => ({
            ...prev,
            username: { 
              available: data.available, 
              checking: false, 
              message: data.message
            }
          }));
        } else {
          throw new Error('Failed to check username availability');
        }
      } catch (error) {
        // If endpoint doesn't exist yet, we'll do basic validation only
        console.log('Username check endpoint not available, using basic validation');
        setAvailability(prev => ({
          ...prev,
          username: { available: true, checking: false, message: 'Username format is valid' }
        }));
      }
    }, 800), // Increased debounce time to reduce API calls
    []
  );

  const validatePassword = (password: string): PasswordValidation => {
    const hasMinLength = password.length >= 8;
    const hasUppercase = /[A-Z]/.test(password);
    const hasLowercase = /[a-z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    const validations = [hasMinLength, hasUppercase, hasLowercase, hasNumber, hasSpecialChar];
    const score = validations.filter(Boolean).length;

    let strength: 'weak' | 'medium' | 'strong' = 'weak';
    if (score >= 4) strength = 'medium';
    if (score === 5) strength = 'strong';

    return {
      hasMinLength,
      hasUppercase,
      hasLowercase,
      hasNumber,
      hasSpecialChar,
      score,
      strength
    };
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    const trimmedValue = value.trim();
    setFormData({ ...formData, [id]: trimmedValue });

    if (id === 'password') {
      setPasswordValidation(validatePassword(trimmedValue));
    } else if (id === 'email') {
      checkEmailAvailability(trimmedValue);
    } else if (id === 'username') {
      checkUsernameAvailability(trimmedValue);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!formData.username || !formData.email || !formData.password) {
      return setErrorMessage('Please fill out all fields.');
    }

    // Frontend validation before sending to backend
    if (formData.password && passwordValidation.score < 5) {
      return setErrorMessage('Please make sure your password meets all requirements.');
    }

    // Check if username meets requirements
    if (formData.username) {
      if (formData.username.length < 6 || formData.username.length > 40) {
        return setErrorMessage('Username must be between 6 and 40 characters.');
      }
      if (formData.username !== formData.username.toLowerCase()) {
        return setErrorMessage('Username must be lowercase.');
      }
      if (!/^[a-z0-9]+$/.test(formData.username)) {
        return setErrorMessage('Username can only contain letters and numbers.');
      }
    }

    // Check email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      return setErrorMessage('Please enter a valid email address.');
    }

    try {
      setLoading(true);
      setErrorMessage(null);
      
      const res = await apiInterceptor.request('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(formData),
      });
      
      const data = await res.json();
      
      if (res.ok) {
        setLoading(false);
        router.push('/sign-in');
      } else {
        setErrorMessage(data.detail || data.message || 'Signup failed. Please try again.');
        setLoading(false);
      }
    } catch (error: any) {
      // Handle specific backend errors
      if (error.message?.includes('Email already exists') || error.detail?.includes('Email already exists')) {
        setErrorMessage('This email is already registered. Please use a different email.');
      } else if (error.message?.includes('Username already exists') || error.detail?.includes('Username already exists')) {
        setErrorMessage('This username is already taken. Please choose a different username.');
      } else {
        setErrorMessage(error.message || error.detail || 'Something went wrong. Please try again.');
      }
      setLoading(false);
    }
  };

  const getStrengthColor = () => {
    switch (passwordValidation.strength) {
      case 'weak': return 'red';
      case 'medium': return 'yellow';
      case 'strong': return 'green';
      default: return 'red';
    }
  };

  const getStrengthText = () => {
    switch (passwordValidation.strength) {
      case 'weak': return 'Weak';
      case 'medium': return 'Medium';
      case 'strong': return 'Strong';
      default: return 'Weak';
    }
  };

  const ValidationItem = ({ valid, text }: { valid: boolean; text: string }) => (
    <div className={`flex items-center text-sm ${valid ? 'text-green-600' : 'text-red-600'}`}>
      {valid ? <HiCheck className="w-4 h-4 mr-2" /> : <HiX className="w-4 h-4 mr-2" />}
      {text}
    </div>
  );

  const AvailabilityIndicator = ({ type }: { type: 'email' | 'username' }) => {
    const status = availability[type];
    
    if (!formData[type]) return null;
    
    if (status.checking) {
      return (
        <div className="flex items-center text-sm text-blue-600 mt-1">
          <Spinner size="sm" />
          <span className="ml-2">{status.message}</span>
        </div>
      );
    }
    
    if (status.message) {
      return (
        <div className={`flex items-center text-sm mt-1 ${
          status.available ? 'text-green-600' : 'text-red-600'
        }`}>
          {status.available ? <HiCheck className="w-4 h-4 mr-2" /> : <HiExclamation className="w-4 h-4 mr-2" />}
          <span>{status.message}</span>
        </div>
      );
    }
    
    return null;
  };

  // Cleanup debounced functions
  useEffect(() => {
    return () => {
      checkEmailAvailability.cancel();
      checkUsernameAvailability.cancel();
    };
  }, [checkEmailAvailability, checkUsernameAvailability]);

  const isFormValid = 
    formData.username && 
    formData.email && 
    formData.password && 
    passwordValidation.score === 5 &&
    formData.username.length >= 6 &&
    formData.username === formData.username.toLowerCase() &&
    /^[a-z0-9]+$/.test(formData.username) &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email);

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
                Sign up to get started
              </p>
            </div>

            <form className='flex flex-col gap-4' onSubmit={handleSubmit}>
              {/* Username Field */}
              <div className='space-y-2'>
                <div className="flex items-center gap-2">
                  <Label htmlFor='username' value='Username' />
                  <Tooltip content="Username must be 6-40 characters, lowercase, and alphanumeric">
                    <HiInformationCircle className="w-4 h-4 text-gray-400 cursor-help" />
                  </Tooltip>
                </div>
                <TextInput
                  type='text'
                  placeholder='Enter your username (6-40 characters)'
                  id='username'
                  onChange={handleChange}
                  required
                  shadow
                />
                <AvailabilityIndicator type="username" />
              </div>
              
              {/* Email Field */}
              <div className='space-y-2'>
                <Label htmlFor='email' value='Email Address' />
                <TextInput
                  type='email'
                  placeholder='name@company.com'
                  id='email'
                  onChange={handleChange}
                  required
                  shadow
                />
                <AvailabilityIndicator type="email" />
              </div>
              
              {/* Password Field */}
              <div className='space-y-3'>
                <div className="flex items-center gap-2">
                  <Label htmlFor='password' value='Password' />
                  <Tooltip content="Password must meet all requirements below">
                    <HiInformationCircle className="w-4 h-4 text-gray-400 cursor-help" />
                  </Tooltip>
                </div>
                
                <div className="relative">
                  <TextInput
                    type={showPassword ? 'text' : 'password'}
                    placeholder='Create a strong password'
                    id='password'
                    onChange={handleChange}
                    required
                    shadow
                    className="pr-12"
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 text-sm font-medium"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? 'Hide' : 'Show'}
                  </button>
                </div>

                {/* Password Strength Indicator */}
                {formData.password && (
                  <div className="space-y-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Password Strength:
                      </span>
                      <span className={`text-sm font-semibold ${
                        passwordValidation.strength === 'weak' ? 'text-red-600' :
                        passwordValidation.strength === 'medium' ? 'text-yellow-600' : 'text-green-600'
                      }`}>
                        {getStrengthText()}
                      </span>
                    </div>
                    
                    <Progress 
                      progress={passwordValidation.score * 20} 
                      color={getStrengthColor()}
                      size="sm"
                    />
                    
                    <div className="grid grid-cols-1 gap-2">
                      <ValidationItem valid={passwordValidation.hasMinLength} text="At least 8 characters" />
                      <ValidationItem valid={passwordValidation.hasUppercase} text="One uppercase letter (A-Z)" />
                      <ValidationItem valid={passwordValidation.hasLowercase} text="One lowercase letter (a-z)" />
                      <ValidationItem valid={passwordValidation.hasNumber} text="One number (0-9)" />
                      <ValidationItem valid={passwordValidation.hasSpecialChar} text="One special character (!@#$% etc.)" />
                    </div>
                  </div>
                )}
              </div>

              {/* Submit Button */}
              <Button
                color="purple"
                type='submit'
                disabled={loading || !isFormValid}
                className='w-full mt-4 transition-all duration-200 hover:shadow-lg disabled:opacity-50'
                size='lg'
              >
                {loading ? (
                  <>
                    <Spinner size='sm' />
                    <span className='pl-3'>Creating Account...</span>
                  </>
                ) : (
                  'Sign Up'
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
            <Alert className='mt-4' color='failure'>
              <span className='font-medium'>Error!</span> {errorMessage}
            </Alert>
          )}
        </div>
      </div>
    </div>
  );
}