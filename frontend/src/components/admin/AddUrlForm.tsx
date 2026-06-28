import { useState } from 'react';
import { Spinner } from '../common/Spinner';

interface Props {
  onAdd: (url: string, label: string) => Promise<unknown>;
  busy: boolean;
}

export const AddUrlForm = ({ onAdd, busy }: Props) => {
  const [url, setUrl] = useState('');
  const [label, setLabel] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onAdd(url, label);
    setUrl('');
    setLabel('');
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <label className="label" htmlFor="url-label" style={{ color: 'var(--text-muted)' }}>Label</label>
          <input
            id="url-label"
            className="field"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder="LinkedIn"
            required
            maxLength={100}
          />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <label className="label" htmlFor="url-href" style={{ color: 'var(--text-muted)' }}>URL</label>
          <input
            id="url-href"
            className="field"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://linkedin.com/in/…"
            required
          />
        </div>
      </div>
      <div>
        <button type="submit" className="btn btn-gold" disabled={busy} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {busy ? <><Spinner /> Indexing…</> : 'Add & index →'}
        </button>
      </div>
    </form>
  );
};
