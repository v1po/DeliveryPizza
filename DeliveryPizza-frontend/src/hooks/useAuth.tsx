import axios from "axios";
import React, { useContext, useEffect, useState } from "react";

export type UserData = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  last_login: string | null;
};

type AuthState = {
  user: UserData | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  login: (payload: { email: string; password: string }) => Promise<void>;
  logout: () => Promise<void>;
  register: (payload: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone?: string;
  }) => Promise<void>;
};

const AuthContext = React.createContext<AuthState | null>(null);

const AUTH_API = "/api/v1/auth";
const ACCESS_TOKEN_KEY = "accessToken";
const REFRESH_TOKEN_KEY = "refreshToken";

const getAuthHeaders = (token: string | null) =>
  token ? { Authorization: `Bearer ${token}` } : undefined;

const AuthProvider: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  const [user, setUser] = useState<UserData | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const isAuthenticated = Boolean(accessToken && user);

  const saveTokens = (access: string, refresh: string | null) => {
    setAccessToken(access);
    setRefreshToken(refresh);
    axios.defaults.headers.common.Authorization = `Bearer ${access}`;
    localStorage.setItem(ACCESS_TOKEN_KEY, access);
    if (refresh) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
    }
  };

  const clearAuth = () => {
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
    delete axios.defaults.headers.common.Authorization;
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  };

  const refreshSession = async (refresh: string) => {
    const response = await axios.post(`${AUTH_API}/refresh`, {
      refresh_token: refresh,
    });
    const data = response.data.data;
    saveTokens(data.access_token, data.refresh_token);
    return data.access_token;
  };

  const fetchProfile = async (token: string) => {
    const response = await axios.get(`${AUTH_API}/me?access_token=${encodeURIComponent(token)}`, {
      headers: getAuthHeaders(token),
    });
    setUser(response.data.data);
  };

  useEffect(() => {
    const access = localStorage.getItem(ACCESS_TOKEN_KEY);
    const refresh = localStorage.getItem(REFRESH_TOKEN_KEY);

    const restoreAuth = async () => {
      if (!access) {
        return;
      }

      setAccessToken(access);
      setRefreshToken(refresh);
      axios.defaults.headers.common.Authorization = `Bearer ${access}`;

      try {
        await fetchProfile(access);
      } catch {
        if (refresh) {
          try {
            const newAccess = await refreshSession(refresh);
            await fetchProfile(newAccess);
            return;
          } catch {
            clearAuth();
            return;
          }
        }

        clearAuth();
      }
    };

    void restoreAuth();
  }, []);

  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const config = error.config;
        if (!config || config._retry || !refreshToken) {
          return Promise.reject(error);
        }

        if (error.response?.status === 401) {
          const url = config.url?.toString() || "";
          if (url.includes("/api/v1/auth/login") || url.includes("/api/v1/auth/register") || url.includes("/api/v1/auth/refresh")) {
            clearAuth();
            return Promise.reject(error);
          }

          config._retry = true;
          try {
            const newAccess = await refreshSession(refreshToken);
            config.headers = {
              ...config.headers,
              Authorization: `Bearer ${newAccess}`,
            };
            return axios(config);
          } catch {
            clearAuth();
            return Promise.reject(error);
          }
        }

        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, [refreshToken]);

  const login = async (payload: { email: string; password: string }) => {
    const normalizedEmail = payload.email.trim().toLowerCase();
    const response = await axios.post(`${AUTH_API}/login`, {
      ...payload,
      email: normalizedEmail,
    });
    const data = response.data.data;
    saveTokens(data.access_token, data.refresh_token);
    await fetchProfile(data.access_token);
  };

  const register = async (payload: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone?: string;
  }) => {
    const normalizedEmail = payload.email.trim().toLowerCase();
    await axios.post(`${AUTH_API}/register`, {
      ...payload,
      email: normalizedEmail,
    });
    await login({ email: normalizedEmail, password: payload.password });
  };

  const logout = async () => {
    if (!accessToken) {
      clearAuth();
      return;
    }

    try {
      await axios.post(
        `${AUTH_API}/logout`,
        { refresh_token: refreshToken },
        { headers: getAuthHeaders(accessToken) }
      );
    } catch {
      // ignore logout errors, still clear local state
    }

    clearAuth();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        accessToken,
        refreshToken,
        isAuthenticated,
        login,
        logout,
        register,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = (): AuthState => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuthContext must be used within AuthProvider");
  }
  return ctx;
};

export { AuthProvider };
