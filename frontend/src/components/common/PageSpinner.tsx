export const PageSpinner = () => (
  <div
    style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}
  >
    <div
      style={{
        width: '24px',
        height: '24px',
        border: '1.5px solid var(--border-2)',
        borderTopColor: 'var(--accent)',
        borderRadius: '50%',
        animation: 'rotate-arc 0.8s linear infinite',
      }}
    />
  </div>
);
