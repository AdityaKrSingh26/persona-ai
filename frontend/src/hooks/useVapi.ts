import { useState, useRef, useEffect, useCallback } from 'react';
import VapiSDK from '@vapi-ai/web';

// CJS interop: Vite wraps the module, actual class is at .default when bundled
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const VapiClass: typeof VapiSDK = (VapiSDK as any).default ?? VapiSDK;

export type VapiStatus = 'idle' | 'connecting' | 'active' | 'error';

export interface TranscriptEntry {
  role: 'user' | 'assistant';
  text: string;
}

const PUBLIC_KEY = import.meta.env.VITE_VAPI_PUBLIC_KEY as string;
const ASSISTANT_ID = import.meta.env.VITE_VAPI_ASSISTANT_ID as string;

export const useVapi = () => {
  const vapiRef = useRef<VapiSDK | null>(null);
  const [status, setStatus] = useState<VapiStatus>('idle');
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);

  useEffect(() => {
    const vapi = new VapiClass(PUBLIC_KEY);
    vapiRef.current = vapi;

    vapi.on('call-start', () => setStatus('active'));
    vapi.on('call-end', () => setStatus('idle'));
    vapi.on('error', () => { setStatus('error'); setTimeout(() => setStatus('idle'), 3000); });

    vapi.on('message', (msg: any) => {
      if (msg?.type !== 'transcript' || msg.transcriptType !== 'final') return;
      const role: TranscriptEntry['role'] = msg.role === 'user' ? 'user' : 'assistant';
      let text = msg.transcript || '';
      // Correct phonetic transcription errors for Aditya's name
      text = text.replace(/\ba DTS\b/gi, "Aditya's").replace(/\bDTS\b/gi, "Aditya's");
      setTranscript((prev) => [...prev, { role, text }]);
    });

    return () => {
      vapi.removeAllListeners();
      vapi.stop();
    };
  }, []);

  const start = useCallback(async () => {
    setStatus('connecting');
    setTranscript([]);
    try {
      await vapiRef.current?.start(ASSISTANT_ID);
    } catch {
      setStatus('error');
    }
  }, []);

  const stop = useCallback(() => {
    vapiRef.current?.stop();
  }, []);

  return { status, transcript, start, stop, vapiRef };
};
