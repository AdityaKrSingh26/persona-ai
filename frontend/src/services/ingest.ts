import { api } from './api';
import type { Source } from '../types/source';

export const ingestApi = {
  addUrl: async (url: string, label: string): Promise<Source> => {
    const res = await api.post('/ingest/url', { url, label });
    return res.data;
  },
  uploadResume: async (file: File): Promise<Source> => {
    const form = new FormData();
    form.append('file', file);
    const res = await api.post('/ingest/resume', form);
    return res.data;
  },
  reindex: async (id: string): Promise<Source> => {
    const res = await api.post(`/ingest/${id}/reindex`);
    return res.data;
  },
  list: async (): Promise<Source[]> => {
    const res = await api.get('/sources');
    return res.data;
  },
  remove: async (id: string): Promise<void> => {
    await api.delete(`/sources/${id}`);
  },
};
