import { api } from './api';

export const authApi = {
  login: (password: string) => api.post('/auth/login', { password }),
  me: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
};
