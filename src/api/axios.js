// src/api/axios.js
import axios from 'axios';
import { fetchAuthSession } from 'aws-amplify/auth';

// !!IMPORTANT!! Replace baseURL with the "Invoke URL" you get after deploying your API Gateway
// Example: 'https://xxxxxx.execute-api.ap-southeast-2.amazonaws.com/prod'
const apiClient = axios.create({
  baseURL: 'https://oktjqc9h7i.execute-api.ap-southeast-2.amazonaws.com/stage1',
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json'
  }
});

// Create a request interceptor
apiClient.interceptors.request.use(async (config) => {
  try {
    // Get current user session from Amplify
    const { idToken } = (await fetchAuthSession()).tokens ?? {};
    if (idToken) {
      // If token exists, add it to Authorization header
      config.headers.Authorization = `Bearer ${idToken.toString()}`;
      console.log('API request with authentication token');
    } else {
      console.log('API request without authentication token');
    }
    return config;
  } catch (e) {
    console.log("User not logged in or session expired.");
    return config;
  }
}, (error) => {
  return Promise.reject(error);
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      console.error('Unauthorized request - redirecting to login');
      // You can handle global unauthorized errors here
    }
    return Promise.reject(error);
  }
);

export default apiClient;
