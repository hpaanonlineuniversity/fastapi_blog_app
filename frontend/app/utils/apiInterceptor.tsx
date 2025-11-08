// utils/apiInterceptor.ts

interface RequestOptions extends RequestInit {
  headers?: Record<string, string>;
}

interface FailedRequest {
  resolve: (value: Response | PromiseLike<Response>) => void;
  reject: (reason?: any) => void;
  originalUrl: string;
  originalOptions: RequestOptions;
}

class ApiInterceptor {
  private isRefreshing: boolean;
  private failedRequests: FailedRequest[];

  constructor() {
    this.isRefreshing = false;
    this.failedRequests = [];
  }

  async request(url: string, options: RequestOptions = {}): Promise<Response> {
    const config: RequestInit = {
      ...options,
      credentials: 'include' as RequestCredentials,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      // ✅ 401 Error - Silent refresh (no console log)
      if (response.status === 401 && !url.includes('/auth/')) {
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
        // ✅ Retry all failed requests silently
        this.retryFailedRequests();
        
        // ✅ IMPORTANT: Use this.request() instead of fetch()
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
    // ✅ Use this.request() for all retries to avoid console logs
    this.failedRequests.forEach(({ resolve, reject, originalUrl, originalOptions }) => {
      this.request(originalUrl, originalOptions)
        .then(resolve)
        .catch(reject);
    });
    this.failedRequests = [];
  }

  private handleRefreshFailure(): void {
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
}

export const apiInterceptor = new ApiInterceptor();