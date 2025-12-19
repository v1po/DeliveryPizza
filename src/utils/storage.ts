import axios, { AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { CreateOrderRequest, Order, ApiResponse } from '../services/types';

const API_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken
          });
          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        } else {
          redirectToLogin();
        }
      } catch (refreshError) {
        redirectToLogin();
      }
    }
    
    return Promise.reject(error);
  }
);

function redirectToLogin() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/auth'
}