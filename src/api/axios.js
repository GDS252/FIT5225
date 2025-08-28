// src/api/axios.js
import axios from 'axios';
import { fetchAuthSession } from 'aws-amplify/auth';

// !!重要!! 将 baseURL 替换为您 API Gateway 部署后获得的"调用 URL"
// 例如: 'https://xxxxxx.execute-api.ap-southeast-2.amazonaws.com/prod'
const apiClient = axios.create({
  baseURL: 'https://oktjqc9h7i.execute-api.ap-southeast-2.amazonaws.com/stage1',
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json'
  }
});

// 创建一个请求拦截器
apiClient.interceptors.request.use(async (config) => {
  try {
    // 从 Amplify 获取当前用户的会话
    const { idToken } = (await fetchAuthSession()).tokens ?? {};
    if (idToken) {
      // 如果令牌存在，将其添加到 Authorization 请求头中
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

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      console.error('Unauthorized request - redirecting to login');
      // 可以在这里处理全局的未授权错误
    }
    return Promise.reject(error);
  }
);

export default apiClient;
