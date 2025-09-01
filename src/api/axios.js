// src/api/axios.js
import axios from 'axios';
import { fetchAuthSession } from 'aws-amplify/auth';

// !!IMPORTANT!! Replace baseURL with the "Invoke URL" you get after deploying your API Gateway
// Example: 'https://xxxxxx.execute-api.ap-southeast-2.amazonaws.com/prod'
const apiClient = axios.create({
  baseURL: 'https://oktjqc9h7i.execute-api.ap-southeast-2.amazonaws.com/stage1',
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    // 移除 Cache-Control 头，因为API Gateway CORS没有配置允许这个头
  }
});

// Create a request interceptor
apiClient.interceptors.request.use(async (config) => {
  console.log('🚀 [API] Processing request:', {
    method: config.method?.toUpperCase(),
    url: config.url,
    baseURL: config.baseURL
  });

  try {
    // Ensure headers object exists
    if (!config.headers) {
      config.headers = {};
    }
    
    // Public endpoints that don't require authentication
    const publicEndpoints = ['/subscribe'];
    const isPublicEndpoint = publicEndpoints.some(endpoint => config.url?.includes(endpoint));
    
    if (isPublicEndpoint) {
      console.log('🌐 [API] Public endpoint - skipping authentication');
      delete config.headers.Authorization;
    } else {
      // Get current user session from Amplify for protected endpoints
      console.log('🔐 [API] Protected endpoint - checking authentication');
      const session = await fetchAuthSession();
      const idToken = session?.tokens?.idToken;
      
      if (idToken) {
        // If token exists, add it to Authorization header
        config.headers.Authorization = `Bearer ${idToken.toString()}`;
        console.log('✅ [API] Request authenticated with token');
      } else {
        console.log('⚠️ [API] No authentication token available');
        // Remove authorization header if no token
        delete config.headers.Authorization;
      }
    }
    
    // 移除可能导致CORS问题的额外头
    // config.headers['X-Requested-With'] = 'XMLHttpRequest';
    
    console.log('📤 [API] Final request headers:', Object.keys(config.headers));
    return config;
  } catch (e) {
    console.warn("⚠️ [API] Authentication check failed:", e.message);
    // Ensure headers exist even on error
    if (!config.headers) {
      config.headers = {};
    }
    delete config.headers.Authorization;
    return config;
  }
}, (error) => {
  console.error('❌ [API] Request interceptor error:', error);
  return Promise.reject(error);
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ [API] Response received:', {
      status: response.status,
      statusText: response.statusText,
      url: response.config?.url,
      method: response.config?.method?.toUpperCase(),
      dataSize: JSON.stringify(response.data || {}).length
    });
    
    // Log response data for debugging (limit size to avoid console spam)
    const dataStr = JSON.stringify(response.data || {});
    if (dataStr.length < 1000) {
      console.log('📄 [API] Response data:', response.data);
    } else {
      console.log('📄 [API] Response data (truncated):', dataStr.substring(0, 500) + '...');
    }
    
    return response;
  },
  (error) => {
    console.error('❌ [API] Request failed:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      method: error.config?.method?.toUpperCase(),
      message: error.message
    });
    
    // Log detailed error information
    if (error.response?.data) {
      console.error('📄 [API] Error response data:', error.response.data);
    }
    
    if (error.response?.status === 401) {
      console.error('🔐 [API] Unauthorized - user needs to login again');
      // You can handle global unauthorized errors here
    } else if (error.response?.status === 403) {
      console.error('🚫 [API] Forbidden - user lacks permission');
    } else if (error.response?.status === 404) {
      console.error('🔍 [API] Not found - endpoint may not exist');
    } else if (error.response?.status === 500) {
      console.error('💥 [API] Server error - backend issue');
    } else if (!error.response) {
      console.error('🌐 [API] Network error - possibly CORS or connectivity issue');
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
