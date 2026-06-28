import { useRef } from 'react';
import { Link } from 'react-router-dom';
import { useVapi } from '../hooks/useVapi';
import { VoiceButton } from '../components/voice/VoiceButton';
import { StatusIndicator } from '../components/voice/StatusIndicator';
import { TranscriptPanel } from '../components/voice/TranscriptPanel';

const GitHubIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
    <path d="M9 18c-4.51 2-5-2-7-2" />
  </svg>
);

const LinkedInIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
    <rect x="2" y="9" width="4" height="12" />
    <circle cx="4" cy="4" r="2" />
  </svg>
);

const PortfolioIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="14" x="2" y="7" rx="2" ry="2" />
    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
  </svg>
);

const EmailIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="16" x="2" y="4" rx="2" />
    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
  </svg>
);

const ResumeIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
    <path d="M14 2v4a2 2 0 0 0 2 2h4" />
    <path d="M8 13h8" />
    <path d="M8 17h8" />
  </svg>
);

const AdminIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
  </svg>
);

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
          gap: '24px',
          flexWrap: 'wrap',
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

        {/* Social & Professional Links Dock */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '20px',
            flexWrap: 'wrap',
          }}
        >
          {/* Social Profiles */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <a
              href="https://github.com/AdityaKrSingh26"
              target="_blank"
              rel="noopener noreferrer"
              className="social-link"
              title="GitHub"
              aria-label="GitHub"
            >
              <GitHubIcon />
            </a>
            <a
              href="https://www.linkedin.com/in/adityakrsingh26/"
              target="_blank"
              rel="noopener noreferrer"
              className="social-link"
              title="LinkedIn"
              aria-label="LinkedIn"
            >
              <LinkedInIcon />
            </a>
            <a
              href="https://myportfolio-three-tawny.vercel.app/"
              target="_blank"
              rel="noopener noreferrer"
              className="social-link"
              title="Personal Portfolio"
              aria-label="Personal Portfolio"
            >
              <PortfolioIcon />
            </a>
            <a
              href="mailto:adityakrsingh2604@gmail.com"
              className="social-link"
              title="Email"
              aria-label="Email"
            >
              <EmailIcon />
            </a>
          </div>

          <div style={{ width: '1px', height: '16px', background: 'var(--border)' }} />

          {/* Download Resume Button */}
          <a
            href="https://drive.google.com/file/d/18RYvS-VwXg3FCtEknUGLp_A4oiAr2xHK/view"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-outline"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '11px',
              padding: '6px 14px',
              textDecoration: 'none',
              borderRadius: '2px',
            }}
          >
            <ResumeIcon />
            <span>Resume</span>
          </a>

          <div style={{ width: '1px', height: '16px', background: 'var(--border)' }} />

          {/* Admin Dashboard Lock Link */}
          <Link
            to="/admin"
            className="social-link"
            title="Admin Dashboard"
            aria-label="Admin Dashboard"
            style={{ display: 'flex', alignItems: 'center' }}
          >
            <AdminIcon />
          </Link>
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
