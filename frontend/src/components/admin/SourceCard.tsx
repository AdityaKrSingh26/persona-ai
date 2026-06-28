import type { Source } from '../../types/source';
import { StatusBadge } from '../common/StatusBadge';
import { Spinner } from '../common/Spinner';

interface Props {
  source: Source;
  onReindex: (id: string) => Promise<void>;
  onRemove: (id: string) => Promise<void>;
  busy?: boolean;
}

const FileIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--text-muted)', flexShrink: 0 }}>
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
  </svg>
);

const LinkIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--text-muted)', flexShrink: 0 }}>
    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
  </svg>
);

export const SourceCard = ({ source, onReindex, onRemove, busy }: Props) => (
  <div className="source-card" style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', animation: 'fade-up 0.2s ease' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
      {source.type === 'resume' ? <FileIcon /> : <LinkIcon />}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', minWidth: 0 }}>
        <span style={{ fontSize: '13px', color: 'var(--text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {source.label}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <StatusBadge status={source.status} />
          <span className="label" style={{ color: 'var(--text-muted)' }}>
            {source.chunk_count} chunks
          </span>
        </div>
        {source.status === 'failed' && source.error && (
          <span style={{ fontSize: '11px', color: 'var(--error)', marginTop: '2px' }}>
            {source.error}
          </span>
        )}
      </div>
    </div>

    <div style={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
      {busy ? (
        <Spinner />
      ) : (
        <>
          <button className="btn btn-outline" style={{ fontSize: '10px', padding: '4px 10px' }} onClick={() => onReindex(source.id)}>
            Re-index
          </button>
          <button className="btn btn-ghost" style={{ fontSize: '10px', color: 'var(--error)', opacity: 0.7 }} onClick={() => onRemove(source.id)}>
            Remove
          </button>
        </>
      )}
    </div>
  </div>
);
