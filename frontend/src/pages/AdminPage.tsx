import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useIngest } from '../hooks/useIngest';
import { useMessages } from '../hooks/useMessages';
import { AddUrlForm } from '../components/admin/AddUrlForm';
import { ResumeUploader } from '../components/admin/ResumeUploader';
import { SourceCard } from '../components/admin/SourceCard';
import { Spinner } from '../components/common/Spinner';
import type { ContactMessage } from '../types/message';

const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <section style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
      <span className="label" style={{ color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{title}</span>
      <div style={{ flex: 1, height: '1px', background: 'var(--border)' }} />
    </div>
    {children}
  </section>
);

const MessageCard = ({ message, onRemove }: { message: ContactMessage; onRemove: (id: string) => Promise<void> }) => {
  const [deleting, setDeleting] = useState(false);
  const handleRemove = async () => {
    setDeleting(true);
    await onRemove(message.id);
    setDeleting(false);
  };
  
  return (
    <div className="source-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px', animation: 'fade-up 0.2s ease', position: 'relative' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
          <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text)' }}>
            {message.visitor_name}
          </span>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            {message.visitor_email}
          </span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
          <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
            {new Date(message.created_at).toLocaleString()}
          </span>
          {deleting ? (
            <Spinner />
          ) : (
            <button className="btn btn-ghost" style={{ fontSize: '10px', color: 'var(--error)', padding: '2px 6px', opacity: 0.7 }} onClick={handleRemove}>
              Delete
            </button>
          )}
        </div>
      </div>
      <div style={{ fontSize: '12px', color: 'var(--text-mid)', background: 'rgba(255,255,255,0.02)', padding: '10px 12px', borderLeft: '2px solid var(--accent)', borderRadius: '2px', whiteSpace: 'pre-wrap', lineHeight: 1.4 }}>
        {message.message}
      </div>
    </div>
  );
};

export const AdminPage = () => {
  const { logout } = useAuth();
  const { sources, busy, busyId, error, addUrl, uploadResume, reindex, remove } = useIngest();
  const { messages, remove: removeMessage, error: messageError } = useMessages();

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
      }}
    >
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1px' }}>
            <span style={{ fontSize: '13px', color: 'var(--text)' }}>Knowledge Base</span>
            <span className="label" style={{ color: 'var(--text-muted)' }}>Admin dashboard</span>
          </div>
        </div>

        <button className="btn btn-ghost" onClick={logout} style={{ fontSize: '11px', letterSpacing: '0.1em' }}>
          Sign out →
        </button>
      </header>

      {/* Content */}
      <main
        style={{
          flex: 1,
          maxWidth: '640px',
          width: '100%',
          margin: '0 auto',
          padding: '48px 40px',
          display: 'flex',
          flexDirection: 'column',
          gap: '48px',
          animation: 'fade-up 0.4s ease both',
        }}
      >
        <Section title="Resume PDF">
          <ResumeUploader onUpload={uploadResume} busy={busy} />
        </Section>

        <Section title="URLs">
          <AddUrlForm onAdd={addUrl} busy={busy} />
        </Section>

        {sources.length > 0 && (
          <Section title="Indexed sources">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {sources.map((source) => (
                <SourceCard
                  key={source.id}
                  source={source}
                  onReindex={reindex}
                  onRemove={remove}
                  busy={busyId === source.id}
                />
              ))}
            </div>
          </Section>
        )}

        {messages.length > 0 && (
          <Section title="Recruiter Messages">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {messages.map((msg) => (
                <MessageCard
                  key={msg.id}
                  message={msg}
                  onRemove={removeMessage}
                />
              ))}
            </div>
          </Section>
        )}

        {(error || messageError) && (
          <div
            style={{
              padding: '12px 16px',
              background: 'var(--error-dim)',
              border: '1px solid rgba(201,76,76,0.2)',
              borderRadius: '2px',
              fontSize: '12px',
              color: 'var(--error)',
              animation: 'fade-in 0.2s ease',
            }}
          >
            {error || messageError}
          </div>
        )}
      </main>
    </div>
  );
};
