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
import { useRouter, useParams } from 'next/navigation';
import { apiInterceptor } from '../utils/apiInterceptor';
import { FormData } from '../types/form';
import { RootState } from '../types/redux';
import { Post } from '../types/post';

export default function UpdatePost() {
  const router = useRouter();
  const params = useParams();
  const postId = params.postId as string;
  const { currentUser, csrfToken } = useSelector((state: RootState) => state.user);
  const [loading, setLoading] = useState<boolean>(false);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [image, setImage] = useState<File | undefined>(undefined);
  const [localPostImage, setLocalPostImage] = useState<string>('');
  const fileRef = useRef<HTMLInputElement>(null);
  const dispatch = useDispatch();
  const [publishError, setPublishError] = useState<string | null>(null);
  const [publishSuccess, setPublishSuccess] = useState<string | null>(null);
  const [freshCsrfToken, setFreshCsrfToken] = useState<string | null>(null);

  // Initialize formData state
  const [formData, setFormData] = useState<FormData>({
    title: '',
    category: 'uncategorized',
    content: '',
    image: ''
  });

  // ✅ CSRF Token Initialization - Use Redux token first
  useEffect(() => {
    let isMounted = true;

    const initializeCsrfToken = async () => {
      if (currentUser) {
        if (csrfToken) {
          // ✅ Use existing token from Redux store
          console.log('✅ Using CSRF token from Redux store for UpdatePost');
          if (isMounted) {
            setFreshCsrfToken(csrfToken);
          }
        } else {
          // ✅ Only fetch new token if not available in Redux
          try {
            console.log('🔄 Fetching CSRF token for UpdatePost...');
            const res = await apiInterceptor.request('/api/auth/csrf-token', {
              method: 'GET',
              credentials: 'include',
            });
            
            if (res.ok && isMounted) {
              const data = await res.json();
              if (data.csrfToken) {
                console.log('✅ New CSRF token received for UpdatePost:', data.csrfToken);
                setFreshCsrfToken(data.csrfToken);
                
                dispatch({
                  type: 'user/setCsrfToken',
                  payload: data.csrfToken
                });
              }
            }
          } catch (error) {
            console.error('Error getting CSRF token for UpdatePost:', error);
          }
        }
      }
    };

    initializeCsrfToken();

    return () => {
      isMounted = false;
    };
  }, [currentUser, csrfToken, dispatch]);

  // Fetch post data on component mount
  useEffect(() => {
    const fetchPost = async () => {
      try {
        setLoading(true);
        setPublishError(null);
        
        // ✅ Add CSRF token to GET request if available
        const headers: Record<string, string> = {};
        const currentCsrfToken = csrfToken || freshCsrfToken;
        
        if (currentCsrfToken) {
          headers['X-CSRF-Token'] = currentCsrfToken;
          console.log('🔄 Fetching post with CSRF token');
        }

        const res = await apiInterceptor.request(`/api/post/getposts?postId=${postId}`, {
          method: 'GET',
          headers,
          credentials: 'include'
        });
        
        if (!res.ok) {
          const errorData = await res.json().catch(() => ({ message: 'Failed to fetch post' }));
          throw new Error(errorData.message || 'Failed to fetch post');
        }
        
        const data = await res.json();
        
        if (!data.posts || data.posts.length === 0) {
          throw new Error('Post not found');
        }

        const post = data.posts[0];
        
        // Check if current user is the author
        if (post.userId !== currentUser?.id) {
          throw new Error('You are not authorized to edit this post');
        }

        setFormData({
          title: post.title || '',
          category: post.category || 'uncategorized',
          content: post.content || '',
          image: post.image || ''
        });
        
        if (post.image) {
          setImagePreview(post.image);
        }
      } catch (error) {
        console.error('Error fetching post:', error);
        setPublishError((error as Error).message);
      } finally {
        setLoading(false);
      }
    };

    if (postId && currentUser) {
      fetchPost();
    }
  }, [postId, currentUser, csrfToken, freshCsrfToken]);

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

  useEffect(() => {
    if (image) {
      handleFileUpload(image);
    }
  }, [image]);

  useEffect(() => {
    // Check if we're in the browser environment before using localStorage
    if (typeof window !== 'undefined') {
      const savedPostImage = localStorage.getItem('postImage');
      if (savedPostImage) {
        setLocalPostImage(savedPostImage);
        setImagePreview(savedPostImage);
        setFormData(prev => ({ ...prev, image: savedPostImage }));
      }
    }
  }, []);

  const handleImageUpload = () => {
    setIsUploading(true);
    setTimeout(() => setIsUploading(false), 1000);
  };

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
          console.log('Post image saved to local storage successfully');
        } catch (error) {
          console.error('Error processing file:', (error as Error).message);
          setPublishError('Error saving post image: ' + (error as Error).message);
        }
      };

      reader.onerror = (error) => {
        console.error('File reading error:', error);
        setPublishError('Error reading file');
      };

      reader.readAsDataURL(image);
    } catch (error) {
      console.error('Error uploading file:', (error as Error).message);
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
    console.log('Post image cleared from local storage');
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setPublishError(null);
    setPublishSuccess(null);

    if (!currentUser) {
      setPublishError('Please sign in to update post');
      router.push('/sign-in?redirect=/update-post');
      return;
    }

    if (!formData.title || !formData.content) {
      return setPublishError('Please provide title and content');
    }

    try {
      setLoading(true);
      
      // ✅ Use CSRF token for the request
      const currentCsrfToken = csrfToken || freshCsrfToken;
      
      if (!currentCsrfToken) {
        throw new Error('Security token not available. Please refresh the page.');
      }

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'X-CSRF-Token': currentCsrfToken,
      };

      console.log('🔄 Updating post with CSRF token:', currentCsrfToken);

      const res = await apiInterceptor.request(`/api/post/updatepost/${postId}/${currentUser.id}`, {
        method: 'PUT',
        headers,
        credentials: 'include',
        body: JSON.stringify({
          title: formData.title,
          content: formData.content,
          category: formData.category,
          image: formData.image,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        // Handle CSRF token errors specifically
        if (res.status === 403 && data.detail?.includes('CSRF')) {
          throw new Error('Security token error. Please refresh the page and try again.');
        }
        throw new Error(data.message || 'Failed to update post');
      }

      setPublishSuccess('Post updated successfully!');
      
      // Clear local storage after successful update
      if (typeof window !== 'undefined') {
        localStorage.removeItem('postImage');
      }
      
      // Redirect to the post page after successful update
      setTimeout(() => {
        router.push(`/post/${data.slug}`);
      }, 1500);

    } catch (error) {
      console.error('Error updating post:', error);
      setPublishError((error as Error).message);
      
      // If it's a CSRF error, suggest refreshing the token
      if ((error as Error).message.includes('CSRF') || (error as Error).message.includes('token')) {
        // Try to get a fresh token
        try {
          console.log('🔄 Attempting to refresh CSRF token after error...');
          const res = await apiInterceptor.request('/api/auth/csrf-token', {
            method: 'GET',
            credentials: 'include',
          });
          
          if (res.ok) {
            const tokenData = await res.json();
            if (tokenData.csrfToken) {
              setFreshCsrfToken(tokenData.csrfToken);
              dispatch({
                type: 'user/setCsrfToken',
                payload: tokenData.csrfToken
              });
              console.log('✅ CSRF token refreshed after error');
            }
          }
        } catch (tokenError) {
          console.error('Error refreshing CSRF token:', tokenError);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading && !formData.title) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Spinner size="xl" className="mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading post data...</p>
        </div>
      </div>
    );
  }

  // Check authorization
  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <Card className="text-center p-8">
          <Alert color="failure" className="mb-4">
            Please sign in to update post
          </Alert>
          <Button onClick={() => router.push('/sign-in?redirect=/update-post')}>
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
              Update Post
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Edit and improve your existing post
            </p>
            <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              Updating as: <span className="font-medium text-purple-600 dark:text-purple-400">{currentUser.username}</span>
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
            {/* Success and Error Alerts */}
            {publishError && (
              <Alert color="failure" className="mb-4" onDismiss={() => setPublishError(null)}>
                {publishError}
              </Alert>
            )}
            {publishSuccess && (
              <Alert color="success" className="mb-4" onDismiss={() => setPublishSuccess(null)}>
                {publishSuccess}
              </Alert>
            )}

            {/* Title & Category Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <div className="mb-2">
                  <Label 
                    htmlFor="title" 
                    value="Post Title" 
                    className="text-lg font-medium text-gray-700 dark:text-white" 
                  />
                </div>
                <TextInput
                  id="title"
                  type="text"
                  placeholder="Enter a compelling title..."
                  required
                  sizing="lg"
                  value={formData.title}
                  onChange={handleChange}
                  disabled={loading}
                  className="text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                />
              </div>
              
              <div>
                <div className="mb-2">
                  <Label 
                    htmlFor="category" 
                    value="Category" 
                    className="text-lg font-medium text-gray-700 dark:text-white" 
                  />
                </div>
                <Select
                  id="category"
                  required
                  sizing="lg"
                  value={formData.category}
                  onChange={handleChange}
                  disabled={loading}
                  className="text-gray-900 dark:text-white"
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
              <div className="mb-2">
                <Label 
                  htmlFor="content" 
                  value="Post Content" 
                  className="text-lg font-medium text-gray-700 dark:text-white" 
                />
              </div>
              <Textarea
                id="content"
                placeholder="Write your post content here... You can use markdown formatting."
                required
                rows={12}
                value={formData.content}
                onChange={handleChange}
                disabled={loading}
                className="resize-y text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              />
            </div>

            {/* Image Upload Section */}
            <div className="space-y-4">
              <div>
                <Label 
                  value="Featured Image" 
                  className="text-lg font-medium text-gray-700 dark:text-white" 
                />
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                  Update the featured image for your post
                </p>
              </div>
              
              <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-6 hover:border-purple-400 dark:hover:border-purple-500 transition-all duration-300 bg-gradient-to-br from-white to-gray-100 dark:from-gray-800 dark:to-gray-900 hover:from-purple-50 hover:to-blue-50 dark:hover:from-gray-750 dark:hover:to-gray-800">
                <div className="flex flex-col lg:flex-row gap-6 items-center">
                  {/* Image Preview */}
                  <div className="flex-1">
                    {imagePreview ? (
                      <div className="relative group">
                        <img
                          src={imagePreview}
                          alt="Preview"
                          className="w-full h-48 lg:h-64 object-cover rounded-lg shadow-lg transition-transform duration-300 group-hover:scale-105"
                        />
                        <button
                          type="button"
                          onClick={clearPostImage}
                          disabled={loading}
                          className="absolute top-2 right-2 bg-red-500 dark:bg-red-600 text-white p-2 rounded-full hover:bg-red-600 dark:hover:bg-red-700 w-8 h-8 flex items-center justify-center text-sm transition-all duration-200 shadow-lg hover:scale-110 disabled:opacity-50"
                        >
                          ×
                        </button>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <div className="text-gray-300 dark:text-gray-600 mb-3 transition-colors duration-300">
                          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <p className="text-gray-400 dark:text-gray-500 font-medium">No image selected</p>
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">Click browse to select an image</p>
                      </div>
                    )}
                  </div>

                  {/* Upload Controls */}
                  <div className="flex-1 space-y-4">
                    <div className="text-center lg:text-left">
                      <div className="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 shadow-sm">
                        <svg className="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <FileInput
                          ref={fileRef}
                          id="image"
                          accept="image/*"
                          onChange={handleImageChange}
                          disabled={loading}
                          className="w-full text-gray-900 dark:text-white border-none focus:ring-0 focus:border-transparent"
                        />
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                        Supported formats: JPG, PNG, GIF, WEBP • Max size: 5MB
                      </p>
                    </div>
                    
                    <Button
                      type="button"
                      color="purple"
                      onClick={handleImageUpload}
                      disabled={!imagePreview || isUploading || loading}
                      className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 border-transparent shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5"
                    >
                      {isUploading ? (
                        <>
                          <Spinner size="sm" className="mr-2" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                          </svg>
                          Update Image
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button
                type="button"
                color="gray"
                onClick={() => router.back()}
                disabled={loading}
                className="sm:w-auto w-full"
                size="lg"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Cancel
              </Button>

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
                    Updating...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Update Post
                  </>
                )}
              </Button>
            </div>
          </form>
        </Card>

        {/* Help Text */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Need help? Check out our{' '}
            <a href="#" className="text-purple-600 dark:text-purple-400 hover:underline">
              writing guidelines
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}