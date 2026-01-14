export interface RegisterData {
  email: string;
  password: string;
  username?: string;
  full_name?: string;
  phone?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  message: string;
  data: {
    access_token: string;
    refresh_token: string;
    expires_in: number;
  };
}

export interface UserResponse {
  id: number;
  email: string;
  username?: string;
  full_name?: string;
  phone?: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

class AuthService {
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_AUTH_SERVICE_URL || 'http://localhost:8001';
  }

  async register(data: RegisterData): Promise<UserResponse> {
    const response = await fetch(`${this.baseURL}/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Registration failed');
    }

    const result = await response.json();
    return result.data;
  }

  async login(data: LoginData): Promise<AuthResponse> {
    const response = await fetch(`${this.baseURL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Login failed');
    }

    return response.json();
  }

  async logout(refreshToken: string): Promise<void> {
    await fetch(`${this.baseURL}/api/v1/auth/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  static saveTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  static getTokens(): { accessToken: string | null; refreshToken: string | null } {
    return {
      accessToken: localStorage.getItem('access_token'),
      refreshToken: localStorage.getItem('refresh_token'),
    };
  }

  static isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }
}

export default new AuthService();