import { useEffect, useState } from 'react';
import { authService } from '../utils/auth';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
    
    const handleStorageChange = () => {
      checkAuth();
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const checkAuth = () => {
    const isValid = authService.isTokenValid();
    const userInfo = authService.getUserFromToken();
    
    setIsAuthenticated(isValid);
    setUser(userInfo);
    setLoading(false);
  };

  const login = (accessToken: string, refreshToken: string, userData?: any) => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData));
    }
    checkAuth();
  };

  const logout = () => {
    authService.logout();
  };

  return {
    isAuthenticated,
    user,
    loading,
    login,
    logout,
    checkAuth
  };
};