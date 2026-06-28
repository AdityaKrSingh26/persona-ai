import { useEffect, useRef } from 'react';
import type { TranscriptEntry } from '../../hooks/useVapi';

interface Props {
  entries: TranscriptEntry[];
}

export const TranscriptPanel = ({ entries }: Props) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [entries.length]);

  if (entries.length === 0) return null;

  return (
    <div
      className="transcript-panel"
      style={{
        width: '100%',
        maxWidth: '480px',
        maxHeight: '280px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        padding: '16px',
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: '2px',
      }}
    >
      {entries.map((e, i) => (
        <div
          key={i}
          className="transcript-entry"
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: e.role === 'user' ? 'flex-end' : 'flex-start',
            gap: '3px',
          }}
        >
          <span className="label" style={{ color: e.role === 'user' ? 'var(--accent)' : 'var(--text-muted)' }}>
            {e.role === 'user' ? 'YOU' : 'ADITYA'}
          </span>
          <div
            style={{
              maxWidth: '85%',
              padding: '8px 12px',
              background: e.role === 'user' ? 'var(--accent-dim)' : 'var(--surface-2)',
              border: `1px solid ${e.role === 'user' ? 'var(--accent-ring)' : 'var(--border)'}`,
              borderRadius: '2px',
              fontSize: '13px',
              color: 'var(--text)',
              lineHeight: '1.5',
            }}
          >
            {e.text}
          </div>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
};
