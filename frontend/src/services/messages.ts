import { api } from './api';
import type { ContactMessage } from '../types/message';

export const messagesApi = {
  list: async (): Promise<ContactMessage[]> => {
    const res = await api.get('/messages');
    return res.data;
  },
  remove: async (id: string): Promise<void> => {
    await api.delete(`/messages/${id}`);
  },
};
