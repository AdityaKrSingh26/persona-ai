import type { VapiStatus } from '../../hooks/useVapi';

interface Props {
  status: VapiStatus;
}

const dot: Record<VapiStatus, string> = {
  idle:       '#454039',
  connecting: '#c9a84c',
  active:     '#5fcf80',
  error:      '#c94c4c',
};

const label: Record<VapiStatus, string> = {
  idle:       'READY',
  connecting: 'CONNECTING',
  active:     'LIVE',
  error:      'ERROR',
};

export const StatusIndicator = ({ status }: Props) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
    <div
      style={{
        width: '6px',
        height: '6px',
        borderRadius: '50%',
        background: dot[status],
        boxShadow: status === 'active' ? `0 0 8px ${dot[status]}` : 'none',
        transition: 'background 0.3s, box-shadow 0.3s',
      }}
    />
    <span className="label" style={{ color: dot[status], transition: 'color 0.3s' }}>
      {label[status]}
      {status === 'connecting' && <span className="cursor-blink" />}
    </span>
  </div>
);
