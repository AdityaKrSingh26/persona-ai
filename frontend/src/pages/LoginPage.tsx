import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(password);
      navigate('/admin');
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px 24px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background grid lines */}
      <div
        aria-hidden
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage:
            'linear-gradient(var(--border) 1px, transparent 1px), linear-gradient(90deg, var(--border) 1px, transparent 1px)',
          backgroundSize: '60px 60px',
          opacity: 0.4,
          pointerEvents: 'none',
        }}
      />

      <form
        onSubmit={handleSubmit}
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: '320px',
          display: 'flex',
          flexDirection: 'column',
          gap: '40px',
          animation: 'fade-up 0.5s ease both',
        }}
      >
        {/* Mark */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              border: '1px solid var(--accent)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '12px',
              color: 'var(--accent)',
              letterSpacing: '0.05em',
              marginBottom: '4px',
            }}
          >
            AK
          </div>
          <h1
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '28px',
              fontWeight: 300,
              fontStyle: 'italic',
              color: 'var(--text)',
              lineHeight: 1.1,
            }}
          >
            Admin Access
          </h1>
          <p className="label" style={{ color: 'var(--text-muted)' }}>
            Knowledge base dashboard
          </p>
        </div>

        {/* Fields */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label className="label" htmlFor="pw" style={{ color: 'var(--text-muted)' }}>
              Password
            </label>
            <input
              id="pw"
              className="field"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="···············"
              required
              autoFocus
              autoComplete="current-password"
            />
          </div>

          {error && (
            <p
              style={{
                fontSize: '12px',
                color: 'var(--error)',
                letterSpacing: '0.04em',
                animation: 'fade-in 0.2s ease',
              }}
            >
              {error}
            </p>
          )}

          <button type="submit" className="btn btn-gold" disabled={busy}>
            {busy ? 'Authenticating…' : 'Sign in →'}
          </button>
        </div>
      </form>
    </div>
  );
};
