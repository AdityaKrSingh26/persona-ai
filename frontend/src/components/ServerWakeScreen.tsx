import { useEffect, useRef, useState } from 'react';

const API = import.meta.env.VITE_API_BASE_URL as string;
const POLL_INTERVAL = 10000; // ms between pings
const MAX_WAIT_MS   = 90000; // give up after 90s (Render free tier can be slow)

type Status = 'waking' | 'ready' | 'timeout';

interface Props {
  onReady: () => void;
}

export function ServerWakeScreen({ onReady }: Props) {
  const [status, setStatus]     = useState<Status>('waking');
  const [dots, setDots]         = useState('');
  const [elapsed, setElapsed]   = useState(0);
  const startRef                = useRef(Date.now());
  const timerRef                = useRef<ReturnType<typeof setTimeout> | null>(null);
  const dotRef                  = useRef<ReturnType<typeof setInterval> | null>(null);
  const doneRef                 = useRef(false); // guard against strict-mode double-fire

  // Animated dots
  useEffect(() => {
    dotRef.current = setInterval(() => {
      setDots(d => (d.length >= 3 ? '' : d + '.'));
    }, 450);
    return () => { if (dotRef.current) clearInterval(dotRef.current); };
  }, []);

  // Elapsed counter
  useEffect(() => {
    const id = setInterval(() => setElapsed(Math.floor((Date.now() - startRef.current) / 1000)), 1000);
    return () => clearInterval(id);
  }, []);

  // Health polling
  useEffect(() => {
    if (doneRef.current) return; // strict-mode guard
    let cancelled = false;
    let failCount = 0;

    console.log('[wake] starting poll →', `${API}/health`);

    async function ping() {
      if (cancelled || doneRef.current) return;

      if (Date.now() - startRef.current >= MAX_WAIT_MS) {
        console.warn('[wake] timeout after', MAX_WAIT_MS / 1000, 's');
        setStatus('timeout');
        return;
      }

      const controller = new AbortController();
      const abortTimer = setTimeout(() => controller.abort(), 12000);
      const pingStart = Date.now();

      try {
        console.log('[wake] ping →', `${API}/health`);
        // mode: no-cors — skip CORS preflight, any response = server is up
        await fetch(`${API}/health`, { signal: controller.signal, mode: 'no-cors' });
        clearTimeout(abortTimer);
        console.log('[wake] ✓ server responded');
        if (!cancelled) {
          doneRef.current = true;
          setStatus('ready');
          return;
        }
      } catch (err) {
        clearTimeout(abortTimer);
        const duration = Date.now() - pingStart;
        failCount++;
        console.warn(`[wake] ✗ ping failed (${duration}ms, fail #${failCount}):`, err);

        // If failures are near-instant (<300ms), it's a client-side block (Brave/uBlock).
        // After 3 such fast failures, let the app through — server errors show their own UI.
        if (duration < 300 && failCount >= 3) {
          console.warn('[wake] requests blocked by browser — skipping wake screen');
          if (!cancelled) {
            doneRef.current = true;
            setStatus('ready');
          }
          return;
        }
      }

      if (!cancelled) {
        timerRef.current = setTimeout(ping, POLL_INTERVAL);
      }
    }

    ping();
    return () => {
      cancelled = true;
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  // Fade out then call onReady
  useEffect(() => {
    if (status === 'ready') {
      const id = setTimeout(onReady, 900); // let the fade-out play
      return () => clearTimeout(id);
    }
  }, [status, onReady]);

  const isReady   = status === 'ready';
  const isTimeout = status === 'timeout';

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'var(--bg)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '32px',
        zIndex: 1000,
        transition: 'opacity 0.8s ease',
        opacity: isReady ? 0 : 1,
      }}
    >
      {/* Orb */}
      <div style={{ position: 'relative', width: 72, height: 72 }}>
        {/* Pulsing rings — shown only while waking */}
        {!isReady && !isTimeout && (
          <>
            <span style={{
              position: 'absolute', inset: 0, borderRadius: '50%',
              border: '1px solid var(--accent)',
              animation: 'pulse-ring 2s ease-out infinite',
            }} />
            <span style={{
              position: 'absolute', inset: 0, borderRadius: '50%',
              border: '1px solid var(--accent)',
              animation: 'pulse-ring 2s ease-out infinite',
              animationDelay: '0.6s',
            }} />
          </>
        )}

        {/* Core circle */}
        <div style={{
          position: 'absolute', inset: 12,
          borderRadius: '50%',
          border: `1.5px solid ${isTimeout ? 'var(--error)' : 'var(--accent)'}`,
          background: isTimeout ? 'var(--error-dim)' : 'var(--accent-dim)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          transition: 'border-color 0.3s, background 0.3s',
        }}>
          {/* Spinning arc while waking */}
          {!isReady && !isTimeout && (
            <span style={{
              position: 'absolute', inset: -2,
              borderRadius: '50%',
              border: '1.5px solid transparent',
              borderTopColor: 'var(--accent)',
              animation: 'rotate-arc 1s linear infinite',
            }} />
          )}

          {/* Icon */}
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
            stroke={isTimeout ? 'var(--error)' : 'var(--accent)'}
            strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            {isTimeout
              ? <><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></>
              : <><path d="M12 2a10 10 0 0 1 10 10"/><path d="M12 6v6l4 2"/></>
            }
          </svg>
        </div>
      </div>

      {/* Text block */}
      <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <p style={{
          fontFamily: 'var(--font-display)',
          fontSize: '22px',
          fontWeight: 300,
          color: 'var(--text)',
          letterSpacing: '0.02em',
        }}>
          {isTimeout
            ? 'Server unavailable'
            : isReady
              ? 'Connected'
              : 'Waking server'}
          {!isTimeout && !isReady && (
            <span style={{ display: 'inline-block', width: '18px', textAlign: 'left' }}>{dots}</span>
          )}
        </p>

        <p style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '0.08em' }}>
          {isTimeout
            ? 'Could not reach the backend. Please try refreshing.'
            : isReady
              ? 'Loading your experience'
              : `Free tier — spinning up · ${elapsed}s`}
        </p>

        {/* Progress bar */}
        {!isTimeout && !isReady && (
          <div style={{
            width: 180,
            height: 1,
            background: 'var(--border)',
            margin: '4px auto 0',
            borderRadius: 1,
            overflow: 'hidden',
          }}>
            <div style={{
              height: '100%',
              background: 'linear-gradient(90deg, transparent, var(--accent), transparent)',
              backgroundSize: '200% 100%',
              animation: 'shimmer 1.6s ease-in-out infinite',
            }} />
          </div>
        )}
      </div>

      {/* Retry button on timeout */}
      {isTimeout && (
        <button
          className="btn btn-outline"
          style={{ marginTop: 8 }}
          onClick={() => window.location.reload()}
        >
          Retry
        </button>
      )}
    </div>
  );
}
