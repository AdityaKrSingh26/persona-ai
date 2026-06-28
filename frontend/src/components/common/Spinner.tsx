export const Spinner = () => (
  <span
    style={{
      display: 'inline-block',
      width: '12px',
      height: '12px',
      border: '1.5px solid currentColor',
      borderTopColor: 'transparent',
      borderRadius: '50%',
      animation: 'rotate-arc 0.7s linear infinite',
      verticalAlign: 'middle',
    }}
  />
);
