'use client';
import { Avatar, Button, Card, Label, TextInput, Textarea, FileInput, Alert } from 'flowbite-react';
import { useRef, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiInterceptor } from '../utils/apiInterceptor';
import {
  updateUserStart,
  updateUserSuccess,
  updateUserFailure,
  deleteUserStart,
  deleteUserSuccess,
  deleteUserFailure,
  signOut,
} from '../redux/user/userSlice';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { User, ApiError } from '../types/user';

interface FormData {
  username: string;
  email: string;
  password: string;
  profilePicture: string;
}

export default function PrivateProfile() {
  const { currentUser, loading, error } = useAppSelector((state) => state.user);
  const [image, setImage] = useState<File | undefined>(undefined);
  const [localProfilePic, setLocalProfilePic] = useState<string>(currentUser?.profilePicture || '');
  const [updateSuccess, setUpdateSuccess] = useState<boolean>(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const dispatch = useAppDispatch();

  const [formData, setFormData] = useState<FormData>({
    username: currentUser?.username || '',
    email: currentUser?.email || '',
    password: '',
    profilePicture: currentUser?.profilePicture || ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const updateFormDataWithProfilePic = (profilePic: string) => {
    if (profilePic) {
      setFormData(prevFormData => ({
        ...prevFormData,
        profilePicture: profilePic
      }));
    }
  };

  useEffect(() => {
    if (image) {
      handleFileUpload(image);
    }
  }, [image]);

  useEffect(() => {
    const savedProfilePic = localStorage.getItem('profilePicture');
    if (savedProfilePic) {
      setLocalProfilePic(savedProfilePic);
      updateFormDataWithProfilePic(savedProfilePic);
    }
    
    if (currentUser) {
      setFormData({
        username: currentUser.username || '',
        email: currentUser.email || '',
        password: '',
        profilePicture: currentUser.profilePicture || savedProfilePic || ''
      });
    }
  }, [currentUser]);

  const handleFileUpload = async (image: File) => {
    try {
      if (!image) {
        throw new Error('No file selected');
      }

      const maxSize = 2 * 1024 * 1024;
      if (image.size > maxSize) {
        throw new Error('File size must be less than 2MB');
      }

      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(image.type)) {
        throw new Error('Please select a valid image file (JPEG, PNG, GIF, WebP)');
      }

      const reader = new FileReader();
      
      reader.onload = (event) => {
        try {
          const base64String = event.target?.result as string;
          localStorage.setItem('profilePicture', base64String);
          setLocalProfilePic(base64String);
          updateFormDataWithProfilePic(base64String);
          console.log('Profile picture saved to local storage successfully');
        } catch (error) {
          console.error('Error processing file:', (error as Error).message);
          alert('Error saving profile picture: ' + (error as Error).message);
        }
      };

      reader.onerror = (error) => {
        console.error('File reading error:', error);
        alert('Error reading file');
      };

      reader.readAsDataURL(image);
    } catch (error) {
      console.error('Error uploading file:', (error as Error).message);
      alert((error as Error).message);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
    }
  };

// PrivateProfile component - Add debug logging
const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  try {
    if (!currentUser) {
      dispatch(updateUserFailure({ message: 'No user found' }));
      return;
    }

    console.log('🔄 Making update request...');
    console.log('👤 Current User ID:', currentUser.id);
    console.log('📦 Form Data:', formData);
    
    // Check if cookies are available
    console.log('🍪 Cookies available:', document.cookie ? 'Yes' : 'No');
    console.log('🍪 All cookies:', document.cookie);

    dispatch(updateUserStart());
    const res = await apiInterceptor.request(`/api/user/update/${currentUser.id}`, {
      method: 'PUT',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    console.log('📡 Response Status:', res.status);
    console.log('📡 Response OK:', res.ok);

    const data = await res.json();
    console.log('📡 Response Data:', data);

    if (data.success === false) {
      dispatch(updateUserFailure(data as ApiError));
      return;
    }
    
    dispatch(updateUserSuccess(data as User));
    setUpdateSuccess(true);
    
    setTimeout(() => {
      setUpdateSuccess(false);
    }, 3000);
    
  } catch (error) {
    console.log("❌ Error:", error);
    dispatch(updateUserFailure({ message: (error as Error).message }));
  }
};

  const clearProfilePicture = () => {
    localStorage.removeItem('profilePicture');
    setLocalProfilePic('');
    setFormData(prev => ({ ...prev, profilePicture: '' }));
    console.log('Profile picture cleared from local storage');
  };

  const handleDeleteAccount = async () => {
    if (!currentUser) return;

    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      try {
        dispatch(deleteUserStart());
        const res = await apiInterceptor.request(`/api/user/delete/${currentUser.id}`, {
          method: 'DELETE',
          credentials: 'include',
        });
        const data = await res.json();
        if (data.success === false) {
          dispatch(deleteUserFailure(data as ApiError));
          return;
        }
        dispatch(deleteUserSuccess());
        router.push('/sign-in');
      } catch (error) {
        dispatch(deleteUserFailure({ message: (error as Error).message }));
      }
    }
  };

  const handleSignOut = async () => {
    try {
      const response = await apiInterceptor.request('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
      console.log('Signout response status:', response.status);
      if (response.ok) {
        dispatch(signOut());
        router.push('/sign-in');
      }
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Profile Settings</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Manage your account settings and preferences</p>
        </div>

        {/* Success and Error Messages */}
        {updateSuccess && (
          <Alert color="success" className="mb-6">
            Profile updated successfully!
          </Alert>
        )}
        
        {error && (
        <Alert color="failure" className="mb-6">
          {typeof error === 'string' ? error : error.message || 'Something went wrong!'}
        </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Left Sidebar - Quick Actions */}
            <div className="lg:col-span-1 space-y-6">
              
              {/* Profile Picture Card */}
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Profile Picture</h3>
                <div className="flex flex-col items-center space-y-4">
                  <Avatar
                    img={localProfilePic || currentUser?.profilePicture || "https://flowbite.com/docs/images/people/profile-picture-5.jpg"}
                    alt="Profile picture"
                    size="xl"
                    rounded
                    className="border-4 border-white dark:border-gray-800 shadow-lg"
                  />
                  <div className="text-center">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      JPG, GIF or PNG. Max size 2MB
                    </p>
                    <FileInput 
                      ref={fileRef}
                      accept="image/*"
                      onChange={handleImageChange}
                      className="w-full"
                    />
                  </div>
                  {localProfilePic && (
                    <Button 
                      color="gray" 
                      size="sm" 
                      onClick={clearProfilePicture}
                      className="w-full"
                    >
                      Remove Photo
                    </Button>
                  )}
                </div>
              </Card>

              {/* Account Actions Card */}
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Account Actions</h3>
                <div className="space-y-4">
                  {/* Sign Out Button */}
                  <div className="flex items-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 dark:text-white text-sm">Sign Out</h4>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Secure sign out from your account</p>
                    </div>
                    <Button 
                      color="light" 
                      size="sm"
                      onClick={handleSignOut}
                      disabled={loading}
                      className="border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700"
                    >
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Sign Out
                    </Button>
                  </div>

                  {/* Delete Account Button */}
                  <div className="flex items-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 dark:text-white text-sm">Delete Account</h4>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Permanently delete your account</p>
                    </div>
                    <Button 
                      color="failure" 
                      size="sm"
                      onClick={handleDeleteAccount}
                      disabled={loading}
                      className="hover:bg-red-700 focus:ring-2 focus:ring-red-300 dark:focus:ring-red-900"
                    >
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      Delete
                    </Button>
                  </div>
                </div>
              </Card>
            </div>

            {/* Main Content Area */}
            <div className="lg:col-span-2 space-y-6">
              
              {/* Personal Information Card */}
              <Card>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Personal Information</h3>
                <div className="space-y-6">
                  
                  <div>
                    <Label htmlFor="username" value="Username" />
                    <TextInput
                      id="username"
                      value={formData.username}
                      onChange={handleChange}
                      placeholder="username"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="email" value="Email Address" />
                    <TextInput
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="Enter your email address"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="password" value="New Password" />
                    <TextInput
                      id="password"
                      type="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="Enter new password"
                    />
                  </div>
                  
                  <Button 
                    type="submit" 
                    color="purple" 
                    disabled={loading}
                    className="w-full sm:w-auto"
                  >
                    {loading ? 'Updating...' : 'Save Changes'}
                  </Button>
                </div>
              </Card>

              {/* Additional Information Card (Optional) */}
              <Card>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Additional Information</h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-500 dark:text-gray-400">Account Created:</span>
                      <p className="text-gray-900 dark:text-white">
                        {currentUser?.createdAt ? new Date(currentUser.createdAt).toLocaleDateString() : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-500 dark:text-gray-400">Last Updated:</span>
                      <p className="text-gray-900 dark:text-white">
                        {currentUser?.updatedAt ? new Date(currentUser.updatedAt).toLocaleDateString() : 'N/A'}
                      </p>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}