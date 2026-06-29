import { useState, useEffect, useCallback } from 'react';
import { messagesApi } from '../services/messages';
import type { ContactMessage } from '../types/message';

export const useMessages = () => {
  const [messages, setMessages] = useState<ContactMessage[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setBusy(true);
    try {
      setMessages(await messagesApi.list());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const remove = async (id: string): Promise<void> => {
    setError(null);
    try {
      await messagesApi.remove(id);
      setMessages((prev) => prev.filter((m) => m.id !== id));
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return { messages, busy, error, refresh, remove };
};
