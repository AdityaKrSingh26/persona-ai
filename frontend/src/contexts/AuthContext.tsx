import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { authApi } from '../services/auth';
import { set401Handler } from '../services/api';

type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

interface AuthContextValue {
  status: AuthStatus;
  login: (password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [status, setStatus] = useState<AuthStatus>('loading');

  useEffect(() => {
    authApi.me()
      .then(() => setStatus('authenticated'))
      .catch(() => setStatus('unauthenticated'));

    set401Handler(() => {
      setStatus('unauthenticated');
    });

    return () => {
      set401Handler(null);
    };
  }, []);

  const login = async (password: string) => {
    await authApi.login(password);
    setStatus('authenticated');
  };

  const logout = async () => {
    await authApi.logout();
    setStatus('unauthenticated');
  };

  return (
    <AuthContext.Provider value={{ status, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuthContext must be used inside AuthProvider');
  return ctx;
};
