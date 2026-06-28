import { useRef, useState } from 'react';
import { Spinner } from '../common/Spinner';

interface Props {
  onUpload: (file: File) => Promise<unknown>;
  busy: boolean;
}

const UploadIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" y1="3" x2="12" y2="15" />
  </svg>
);

export const ResumeUploader = ({ onUpload, busy }: Props) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [drag, setDrag] = useState(false);

  const handleFile = async (file: File | undefined) => {
    if (file) await onUpload(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDrag(false);
    handleFile(e.dataTransfer.files[0]);
  };

  return (
    <div
      className={`upload-zone${drag ? ' upload-zone--drag' : ''}`}
      style={{
        padding: '32px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '12px',
        borderRadius: '2px',
        cursor: busy ? 'not-allowed' : 'pointer',
        opacity: busy ? 0.6 : 1,
        minHeight: '140px',
      }}
      onClick={() => !busy && inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,application/pdf"
        onChange={(e) => handleFile(e.target.files?.[0])}
        style={{ display: 'none' }}
      />

      {busy ? (
        <>
          <Spinner />
          <span className="label" style={{ color: 'var(--text-mid)' }}>Parsing & indexing…</span>
        </>
      ) : (
        <>
          <div style={{ color: 'var(--accent)', opacity: 0.7 }}>
            <UploadIcon />
          </div>
          <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontSize: '13px', color: 'var(--text-mid)' }}>
              Drop a PDF or click to browse
            </span>
            <span className="label" style={{ color: 'var(--text-muted)' }}>
              Max 10 MB — one resume at a time
            </span>
          </div>
        </>
      )}
    </div>
  );
};
