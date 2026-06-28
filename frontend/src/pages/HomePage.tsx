import { useRef } from 'react';
import { useVapi } from '../hooks/useVapi';
import { VoiceButton } from '../components/voice/VoiceButton';
import { StatusIndicator } from '../components/voice/StatusIndicator';
import { TranscriptPanel } from '../components/voice/TranscriptPanel';

const hints = [
  'ask about my experience',
  'ask about projects',
  'ask about skills',
  'schedule a meeting',
];

export const HomePage = () => {
  const { status, transcript, start, stop } = useVapi();
  const isIdle = status === 'idle';
  const hint = useRef(hints[Math.floor(Math.random() * hints.length)]).current;

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Radial background glow */}
      <div
        aria-hidden
        style={{
          position: 'absolute',
          top: '35%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '600px',
          height: '600px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(201,168,76,0.04) 0%, transparent 70%)',
          pointerEvents: 'none',
        }}
      />

      {/* Header */}
      <header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '24px 40px',
          borderBottom: '1px solid var(--border)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '28px',
              height: '28px',
              border: '1px solid var(--accent)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '10px',
              color: 'var(--accent)',
              letterSpacing: '0.05em',
            }}
          >
            AK
          </div>
          <span className="label" style={{ color: 'var(--text-mid)' }}>Voice Profile</span>
        </div>

        <StatusIndicator status={status} />
      </header>

      {/* Main */}
      <main
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 24px',
          gap: '48px',
        }}
      >
        {/* Title */}
        <div style={{ textAlign: 'center', animation: 'fade-up 0.6s ease both' }}>
          <h1
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(48px, 8vw, 88px)',
              fontWeight: 300,
              fontStyle: 'italic',
              color: 'var(--text)',
              lineHeight: 1.05,
              letterSpacing: '-0.02em',
            }}
          >
            Aditya Kumar Singh
          </h1>
          <p
            className="label"
            style={{
              marginTop: '12px',
              color: 'var(--text-muted)',
              letterSpacing: '0.18em',
            }}
          >
            Software Engineer — AI Voice Profile
          </p>
        </div>

        {/* Voice interface */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '32px',
            animation: 'fade-up 0.6s 0.1s ease both',
          }}
        >
          <VoiceButton status={status} onStart={start} onStop={stop} />

          <div style={{ textAlign: 'center' }}>
            {isIdle && (
              <p
                style={{
                  color: 'var(--text-muted)',
                  fontSize: '12px',
                  letterSpacing: '0.06em',
                }}
              >
                Press to begin — {hint}
              </p>
            )}
            {status === 'active' && (
              <p style={{ color: 'var(--accent)', fontSize: '12px', letterSpacing: '0.06em' }}>
                Listening — speak naturally
              </p>
            )}
            {status === 'error' && (
              <p style={{ color: 'var(--error)', fontSize: '12px', letterSpacing: '0.06em' }}>
                Connection failed — try again
              </p>
            )}
          </div>
        </div>

        {/* Transcript */}
        <div style={{ animation: 'fade-up 0.3s ease both' }}>
          <TranscriptPanel entries={transcript} />
        </div>
      </main>

      {/* Footer */}
      <footer
        style={{
          padding: '16px 40px',
          borderTop: '1px solid var(--border)',
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <span className="label" style={{ color: 'var(--text-muted)' }}>
          Powered by Vapi · RAG · pgvector
        </span>
      </footer>
    </div>
  );
};
