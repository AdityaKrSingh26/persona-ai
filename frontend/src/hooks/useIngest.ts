import { useState, useEffect, useCallback } from 'react';
import { ingestApi } from '../services/ingest';
import type { Source } from '../types/source';

export const useIngest = () => {
  const [sources, setSources] = useState<Source[]>([]);
  const [busy, setBusy] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setSources(await ingestApi.list());
    } catch {
      // non-fatal
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const addUrl = async (url: string, label: string): Promise<Source | null> => {
    setBusy(true);
    setError(null);
    try {
      const source = await ingestApi.addUrl(url, label);
      await refresh();
      return source;
    } catch (e) {
      setError((e as Error).message);
      return null;
    } finally {
      setBusy(false);
    }
  };

  const uploadResume = async (file: File): Promise<Source | null> => {
    setBusy(true);
    setError(null);
    try {
      const source = await ingestApi.uploadResume(file);
      await refresh();
      return source;
    } catch (e) {
      setError((e as Error).message);
      return null;
    } finally {
      setBusy(false);
    }
  };

  const reindex = async (id: string): Promise<void> => {
    setBusyId(id);
    setError(null);
    try {
      await ingestApi.reindex(id);
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusyId(null);
    }
  };

  const remove = async (id: string): Promise<void> => {
    setBusyId(id);
    setError(null);
    try {
      await ingestApi.remove(id);
      setSources((prev) => prev.filter((s) => s.id !== id));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusyId(null);
    }
  };

  return { sources, busy, busyId, error, addUrl, uploadResume, reindex, remove };
};
