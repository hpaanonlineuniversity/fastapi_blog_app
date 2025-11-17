// utils/apiInterceptor.ts - COMPLETE UPDATED VERSION

interface RequestOptions extends RequestInit {
  headers?: Record<string, string>;
}

interface FailedRequest {
  resolve: (value: Response | PromiseLike<Response>) => void;
  reject: (reason?: any) => void;
  originalUrl: string;
  originalOptions: RequestOptions;
}

// Function to get valid CSRF token from Redux store
const getValidCsrfToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  
  try {
    const store = (window as any).__REDUX_STORE__;
    if (!store) return null;
    
    const state = store.getState();
    const { csrfToken, csrfTokenExpiry } = state.user;
    
    // Check if token exists and hasn't expired (15-minute lifetime)
    if (csrfToken && csrfTokenExpiry && Date.now() < csrfTokenExpiry) {
      return csrfToken;
    }
    
    // Token is expired, clear it
    if (csrfToken && csrfTokenExpiry && Date.now() >= csrfTokenExpiry) {
      store.dispatch({ type: 'user/clearCsrfToken' });
    }
    
    return null;
  } catch (error) {
    return null;
  }
};

class ApiInterceptor {
  private isRefreshing: boolean;
  private failedRequests: FailedRequest[];

  constructor() {
    this.isRefreshing = false;
    this.failedRequests = [];
  }

  async request(url: string, options: RequestOptions = {}): Promise<Response> {
    // Get valid CSRF token (checks expiry automatically)
    const csrfToken = getValidCsrfToken();
    
    const config: RequestInit = {
      ...options,
      credentials: 'include' as RequestCredentials,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    // Add CSRF token to headers if available and not an auth endpoint
    // Auth endpoints (/auth/ ပါတဲ့ url တွေ) မှာ CSRF token မထည့်ဘူး
    if (csrfToken && !url.includes('/auth/')) {
      (config.headers as Record<string, string>)['X-CSRF-Token'] = csrfToken;
    }

    try {
      const response = await fetch(url, config);
      
      // ✅ Handle 401 Error - Silent refresh
      // Access token သက်တမ်းကုန်သွားတဲ့အခါ

      if (response.status === 401 && !url.includes('/auth/')) {
        return await this.handleTokenRefresh(url, options);
      }

      // ✅ Handle 403 Error - CSRF token might be invalid/expired
      if (response.status === 403 && !url.includes('/auth/')) {
        console.log('CSRF token might be invalid, attempting refresh...');
        return await this.handleTokenRefresh(url, options);
      }

      return response;
    } catch (error) {
      // ✅ COMPLETELY SILENT for auth/token errors
      const isSilentError = 
        (error instanceof Error && (
          error.message?.includes('Authentication') || 
          error.message?.includes('Unauthorized') ||
          error.message?.includes('token') ||
          error.name === 'TypeError'
        )) ||
        (error as any).silent;

      if (!isSilentError) {
        console.error('API request failed:', error);
      }
      
      throw error;
    }
  }

  private async handleTokenRefresh(originalUrl: string, originalOptions: RequestOptions): Promise<Response> {
    // Prevent multiple simultaneous refresh attempts
    if (this.isRefreshing) {
      return new Promise((resolve, reject) => {
        this.failedRequests.push({ 
          resolve, 
          reject, 
          originalUrl, 
          originalOptions 
        });
      });
    }

    this.isRefreshing = true;

    try {
      // ✅ Silent refresh token call
      const refreshResponse = await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (refreshResponse.ok) {
        const refreshData = await refreshResponse.json();
        
        // ✅ Update CSRF token in Redux store with new 15-minute expiry
        if (refreshData.csrfToken) {
          const store = (window as any).__REDUX_STORE__;
          if (store) {
            store.dispatch({ 
              type: 'user/setCsrfToken', 
              payload: refreshData.csrfToken 
            });
          }
        }
        
        // ✅ Retry all failed requests silently
        this.retryFailedRequests();
        
        // ✅ Retry the original request with new token
        return await this.request(originalUrl, originalOptions);
      } else {
        // ✅ Silent failure - no console logs
        this.handleRefreshFailure();
        const error = new Error('Authentication failed');
        (error as any).silent = true;
        throw error;
      }
    } catch (error) {
      // ✅ Silent error handling
      this.handleRefreshFailure();
      (error as any).silent = true;
      throw error;
    } finally {
      this.isRefreshing = false;
    }
  }

  private retryFailedRequests(): void {
    // ✅ Use this.request() for all retries to maintain CSRF token handling
    this.failedRequests.forEach(({ resolve, reject, originalUrl, originalOptions }) => {
      this.request(originalUrl, originalOptions)
        .then(resolve)
        .catch(reject);
    });
    this.failedRequests = [];
  }

  private handleRefreshFailure(): void {
    // ✅ Clear expired/invalid CSRF token
    if (typeof window !== 'undefined') {
      const store = (window as any).__REDUX_STORE__;
      if (store) {
        store.dispatch({ type: 'user/clearCsrfToken' });
      }
    }
    
    // ✅ Silent redirect to login - Check if window exists (client-side)
    if (typeof window !== 'undefined' && window.location.pathname !== '/sign-in') {
      window.location.href = '/sign-in';
    }
  }

  // ✅ Helper methods for different HTTP methods
  async get(url: string, options: RequestOptions = {}): Promise<Response> {
    return this.request(url, { ...options, method: 'GET' });
  }

  async post(url: string, data?: any, options: RequestOptions = {}): Promise<Response> {
    return this.request(url, { 
      ...options, 
      method: 'POST', 
      body: data ? JSON.stringify(data) : undefined
    });
  }

  async put(url: string, data?: any, options: RequestOptions = {}): Promise<Response> {
    return this.request(url, { 
      ...options, 
      method: 'PUT', 
      body: data ? JSON.stringify(data) : undefined
    });
  }

  async delete(url: string, options: RequestOptions = {}): Promise<Response> {
    return this.request(url, { ...options, method: 'DELETE' });
  }

  async patch(url: string, data?: any, options: RequestOptions = {}): Promise<Response> {
    return this.request(url, { 
      ...options, 
      method: 'PATCH', 
      body: data ? JSON.stringify(data) : undefined
    });
  }

  // ✅ Utility method to check CSRF token status
  getCsrfTokenStatus(): { isValid: boolean; timeRemaining: number } {
    const token = getValidCsrfToken();
    if (!token) {
      return { isValid: false, timeRemaining: 0 };
    }

    try {
      const store = (window as any).__REDUX_STORE__;
      if (store) {
        const state = store.getState();
        const { csrfTokenExpiry } = state.user;
        if (csrfTokenExpiry) {
          const timeRemaining = Math.max(0, csrfTokenExpiry - Date.now());
          return { 
            isValid: true, 
            timeRemaining: Math.ceil(timeRemaining / 1000) // Convert to seconds
          };
        }
      }
    } catch (error) {
      // Silent error
    }

    return { isValid: false, timeRemaining: 0 };
  }
}

export const apiInterceptor = new ApiInterceptor();