// app/create-post/page.tsx - OPTIMIZED VERSION
'use client';
import { 
  Alert, 
  Button, 
  FileInput, 
  Select, 
  TextInput, 
  Textarea,
  Card,
  Label,
  Spinner
} from 'flowbite-react';
import { useState, useRef, useEffect, ChangeEvent, FormEvent } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useRouter } from 'next/navigation';
import { apiInterceptor } from '../utils/apiInterceptor';
import { RootState } from '../types/redux';
import Image from 'next/image';
import { FormData } from '../types/form';
import { CreatePostResponse } from '../types/post';

export default function CreatePost() {
  const router = useRouter();
  const dispatch = useDispatch();
  const { currentUser, csrfToken, loading: userLoading } = useSelector((state: RootState) => state.user);
  
  const [loading, setLoading] = useState<boolean>(false);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [image, setImage] = useState<File | undefined>(undefined);
  const [localPostImage, setLocalPostImage] = useState<string>('');
  const [publishError, setPublishError] = useState<string | null>(null);
  const [freshCsrfToken, setFreshCsrfToken] = useState<string | null>(null);
  
  const fileRef = useRef<HTMLInputElement>(null);

  const [formData, setFormData] = useState<FormData>({
    title: '',
    category: 'uncategorized',
    content: '',
    image: ''
  });

  // ✅ OPTIMIZED: Use Redux token first, only fetch if needed
  useEffect(() => {
    let isMounted = true;

    const initializeCsrfToken = async () => {
      if (currentUser) {
        if (csrfToken) {
          // ✅ Use existing token from Redux store
          console.log('✅ Using CSRF token from Redux store');
          if (isMounted) {
            setFreshCsrfToken(csrfToken);
          }
        } else {
          // ✅ Only fetch new token if not available in Redux
          try {
            console.log('🔄 Fetching CSRF token (not in store)...');
            const res = await apiInterceptor.request('/api/auth/csrf-token', {
              method: 'GET',
              credentials: 'include',
            });
            
            if (res.ok && isMounted) {
              const data = await res.json();
              if (data.csrfToken) {
                console.log('✅ New CSRF token received:', data.csrfToken);
                setFreshCsrfToken(data.csrfToken);
                
                dispatch({
                  type: 'user/setCsrfToken',
                  payload: data.csrfToken
                });
              }
            }
          } catch (error) {
            console.error('Error getting CSRF token:', error);
          }
        }
      }
    };

    initializeCsrfToken();

    return () => {
      isMounted = false;
    };
  }, [currentUser, csrfToken, dispatch]);

  // ✅ Redirect if not authenticated
  useEffect(() => {
    if (!userLoading && !currentUser) {
      console.log('User not authenticated, redirecting to signin...');
      router.push('/sign-in?redirect=/create-post');
      return;
    }
  }, [currentUser, userLoading, router]);

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
    if (publishError) {
      setPublishError(null);
    }
  };

  const handleImageChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
    }
  };

  // Handle image upload when image state changes
  useEffect(() => {
    if (image) {
      handleFileUpload(image);
    }
  }, [image]);

  // Load saved image from localStorage on component mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedPostImage = localStorage.getItem('postImage');
      if (savedPostImage) {
        setLocalPostImage(savedPostImage);
        setImagePreview(savedPostImage);
        setFormData(prev => ({ ...prev, image: savedPostImage }));
      }
    }
  }, []);

  const handleFileUpload = async (image: File) => {
    try {
      if (!image) {
        throw new Error('No file selected');
      }

      const maxSize = 5 * 1024 * 1024;
      if (image.size > maxSize) {
        throw new Error('File size must be less than 5MB');
      }

      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(image.type)) {
        throw new Error('Please select a valid image file (JPEG, PNG, GIF, WebP)');
      }

      const reader = new FileReader();
      
      reader.onload = (event) => {
        try {
          const base64String = event.target?.result as string;
          if (typeof window !== 'undefined') {
            localStorage.setItem('postImage', base64String);
          }
          setLocalPostImage(base64String);
          setImagePreview(base64String);
          setFormData(prev => ({ ...prev, image: base64String }));
        } catch (error) {
          setPublishError('Error saving post image: ' + (error as Error).message);
        }
      };

      reader.onerror = () => {
        setPublishError('Error reading file');
      };

      reader.readAsDataURL(image);
    } catch (error) {
      setPublishError((error as Error).message);
    }
  };

  const clearPostImage = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('postImage');
    }
    setLocalPostImage('');
    setImagePreview(null);
    setFormData(prev => ({ ...prev, image: '' }));
    if (fileRef.current) {
      fileRef.current.value = '';
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!currentUser) {
      setPublishError('Please sign in to create a post');
      router.push('/sign-in?redirect=/create-post');
      return;
    }

    if (!formData.title.trim() || !formData.content.trim()) {
      setPublishError('Please fill in all required fields');
      return;
    }

    setLoading(true); 
    setPublishError(null);

    console.log('Form Data:', formData);
    console.log('Redux CSRF Token:', csrfToken);
    console.log('Fresh CSRF Token:', freshCsrfToken);
    console.log('User authenticated:', !!currentUser);
    
    try {
      // ✅ PRIORITY: Use Redux token first, then fresh token as fallback
      const currentCsrfToken = csrfToken || freshCsrfToken;
      
      if (!currentCsrfToken) {
        throw new Error('No CSRF token available. Please refresh the page.');
      }

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'X-CSRF-Token': currentCsrfToken,
      };

      console.log('Making request with CSRF token:', currentCsrfToken);

      const res = await apiInterceptor.request('/api/post/create', {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify(formData)
      });

      const responseText = await res.text();
      let data: CreatePostResponse;
      
      try {
        data = JSON.parse(responseText);
      } catch (jsonError) {
        console.error('Error parsing JSON:', jsonError);
        console.error('Raw response:', responseText);
        throw new Error('Invalid server response');
      }

      console.log('Create post response:', data);

      if (!res.ok) {
        if (res.status === 403) {
          if (data.detail?.includes('CSRF')) {
            setPublishError('Security token error. Please refresh the page and try again.');
          } else {
            setPublishError('You do not have permission to create posts.');
          }
          return;
        } else if (res.status === 401) {
          setPublishError('Your session has expired. Please sign in again.');
          router.push('/sign-in?redirect=/create-post');
          return;
        } else if (res.status === 400) {
          setPublishError(data.message || data.detail || 'Please check your input and try again.');
          return;
        } else {
          setPublishError(data.message || data.detail || 'Something went wrong. Please try again.');
          return;
        }
      }

      // Success case
      setPublishError(null);
      
      // Remove image from localStorage
      if (typeof window !== 'undefined') {
        localStorage.removeItem('postImage');
      }
      
      // Redirect to the new post
      if (data.slug) {
        console.log('Post created successfully, redirecting to:', `/post/${data.slug}`);
        router.push(`/post/${data.slug}`);
      } else {
        router.push('/');
      }
    } catch (error: any) {
      console.error('Create post error:', error);
      
      if (error.message?.includes('Network') || error.name === 'TypeError') {
        setPublishError('Network error. Please check your connection and try again.');
      } else if (error.message?.includes('Authentication') || error.message?.includes('Unauthorized')) {
        setPublishError('Authentication failed. Please sign in again.');
        router.push('/sign-in?redirect=/create-post');
      } else if (error.message?.includes('CSRF') || error.message?.includes('token')) {
        setPublishError('Security token error. Please refresh the page and try again.');
      } else {
        setPublishError(error.message || 'Something went wrong. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Loading state
  if (userLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <Card className="text-center p-8">
          <Spinner size="xl" className="mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Checking authentication...</p>
        </Card>
      </div>
    );
  }

  // Not authenticated state
  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <Card className="text-center p-8">
          <Alert color="failure" className="mb-4">
            Please sign in to create a post
          </Alert>
          <Button onClick={() => router.push('/sign-in?redirect=/create-post')}>
            Sign In
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <Card className="shadow-xl bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 dark:text-white mb-2">
              Create New Post
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Share your thoughts and ideas with the world
            </p>
            <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              Posting as: <span className="font-medium text-purple-600 dark:text-purple-400">{currentUser.username}</span>
              {csrfToken ? (
                <span className="ml-2 text-green-600 dark:text-green-400">• Security token ready</span>
              ) : freshCsrfToken ? (
                <span className="ml-2 text-yellow-600 dark:text-yellow-400">• Using fresh token</span>
              ) : (
                <span className="ml-2 text-red-600 dark:text-red-400">• No security token</span>
              )}
            </div>
          </div>

          <form className="flex flex-col gap-6" onSubmit={handleSubmit}>
            {/* Title & Category Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <Label htmlFor="title" value="Post Title" className="text-lg font-medium text-gray-700 dark:text-white" />
                <TextInput
                  id="title"
                  type="text"
                  placeholder="Enter a compelling title..."
                  required
                  sizing="lg"
                  value={formData.title}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>
              
              <div>
                <Label htmlFor="category" value="Category" className="text-lg font-medium text-gray-700 dark:text-white" />
                <Select
                  id="category"
                  required
                  sizing="lg"
                  value={formData.category}
                  onChange={handleChange}
                  disabled={loading}
                >
                  <option value="uncategorized">Select a category</option>
                  <option value="javascript">JavaScript</option>
                  <option value="reactjs">React.js</option>
                  <option value="nextjs">Next.js</option>
                  <option value="webdev">Web Development</option>
                  <option value="programming">Programming</option>
                  <option value="technology">Technology</option>
                </Select>
              </div>
            </div>

            {/* Content */}
            <div>
              <Label htmlFor="content" value="Post Content" className="text-lg font-medium text-gray-700 dark:text-white" />
              <Textarea
                id="content"
                placeholder="Write your post content here..."
                required
                rows={12}
                value={formData.content}
                onChange={handleChange}
                disabled={loading}
              />
            </div>

            {/* Image Upload Section */}
            <div className="space-y-4">
              <div>
                <Label value="Featured Image" className="text-lg font-medium text-gray-700 dark:text-white" />
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                  Add a compelling image to make your post stand out (optional)
                </p>
              </div>
              
              <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-6">
                <div className="flex flex-col lg:flex-row gap-6 items-center">
                  <div className="flex-1">
                    {imagePreview ? (
                      <div className="relative group">
                        <Image
                          src={imagePreview}
                          alt="Preview"
                          width={400}
                          height={300}
                          className="w-full h-48 lg:h-64 object-cover rounded-lg shadow-lg"
                          unoptimized={true}
                        />
                        <button
                          type="button"
                          onClick={clearPostImage}
                          disabled={loading}
                          className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 w-8 h-8 flex items-center justify-center text-sm disabled:opacity-50"
                        >
                          ×
                        </button>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <div className="text-gray-300 dark:text-gray-600 mb-3">
                          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <p className="text-gray-400 dark:text-gray-500 font-medium">No image selected</p>
                      </div>
                    )}
                  </div>

                  <div className="flex-1 space-y-4">
                    <div className="text-center lg:text-left">
                      <div className="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                        <FileInput
                          ref={fileRef}
                          id="image"
                          accept="image/*"
                          onChange={handleImageChange}
                          disabled={loading}
                        />
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                        Supported formats: JPG, PNG, GIF, WEBP • Max size: 5MB
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
              {publishError && (
                <div className="sm:col-span-2">
                  <Alert color="failure" className="mb-4" onDismiss={() => setPublishError(null)}>
                    {publishError}
                  </Alert>
                </div>
              )}

              <Button
                type="submit"
                color="purple"
                disabled={loading}
                className="sm:w-auto w-full"
                size="lg"
              >
                {loading ? (
                  <>
                    <Spinner size="sm" className="mr-2" />
                    Publishing...
                  </>
                ) : (
                  'Publish Post'
                )}
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}