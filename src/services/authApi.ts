import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { User, AuthResponse, ApiResponse } from './types';

const AUTH_URL = import.meta.env.VITE_AUTH_URL || 'http://localhost:8002';

class AuthApi {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: AUTH_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async login(email: string, password: string): Promise<ApiResponse<AuthResponse>> {
    const response: AxiosResponse<ApiResponse<AuthResponse>> = await this.client.post(
      '/auth/login',
      { email, password }
    );
    return response.data;
  }

  async register(email: string, password: string, fullName: string): Promise<ApiResponse<AuthResponse>> {
    const response: AxiosResponse<ApiResponse<AuthResponse>> = await this.client.post(
      '/auth/register',
      { email, password, full_name: fullName }
    );
    return response.data;
  }

  async getProfile(token: string): Promise<ApiResponse<User>> {
    const response: AxiosResponse<ApiResponse<User>> = await this.client.get(
      '/auth/me',
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  }

  async updateProfile(token: string, userData: Partial<User>): Promise<ApiResponse<User>> {
    const response: AxiosResponse<ApiResponse<User>> = await this.client.patch(
      '/auth/me',
      userData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  }
}

export const authApi = new AuthApi();

export default authApi;