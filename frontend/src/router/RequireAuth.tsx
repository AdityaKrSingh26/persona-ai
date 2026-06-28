import type { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { PageSpinner } from '../components/common/PageSpinner';

export const RequireAuth = ({ children }: { children: ReactNode }) => {
  const { status } = useAuth();
  if (status === 'loading') return <PageSpinner />;
  if (status === 'unauthenticated') return <Navigate to="/login" replace />;
  return <>{children}</>;
};
