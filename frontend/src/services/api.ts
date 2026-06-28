import axios from 'axios';

let on401Callback: (() => void) | null = null;

export const set401Handler = (handler: (() => void) | null) => {
  on401Callback = handler;
};

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
  timeout: 120_000,
});

api.interceptors.response.use(
  (r) => r,
  (e) => {
    if (e.response?.status === 401) {
      on401Callback?.();
    }
    return Promise.reject(new Error(e.response?.data?.error ?? 'Unexpected error'));
  },
);
