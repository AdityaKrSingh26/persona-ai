import type { VapiStatus } from '../../hooks/useVapi';

interface Props {
  status: VapiStatus;
  onStart: () => void;
  onStop: () => void;
}

const MicIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a3 3 0 0 1 3 3v7a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3z" />
    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
    <line x1="12" y1="19" x2="12" y2="22" />
  </svg>
);

const StopIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
    <rect x="5" y="5" width="14" height="14" rx="2" />
  </svg>
);

const WaveformBars = ({ status }: { status: VapiStatus }) => {
  const heights = [12, 20, 32, 24, 38, 28, 16, 34, 22, 18, 30];
  const cls = `waveform waveform--${status}`;
  return (
    <div className={cls}>
      {heights.map((h, i) => (
        <div
          key={i}
          className="waveform-bar"
          style={{
            height: `${h}px`,
            animationDelay: `${i * 0.08}s`,
          }}
        />
      ))}
    </div>
  );
};

export const VoiceButton = ({ status, onStart, onStop }: Props) => {
  const active = status === 'active';
  const connecting = status === 'connecting';
  const isOn = active || connecting;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '28px' }}>
      <WaveformBars status={status} />

      <div className="voice-btn-wrap">
        {isOn && (
          <>
            <div className="voice-btn-ring voice-btn-ring--inner" />
            <div className="voice-btn-ring voice-btn-ring--outer" />
          </>
        )}

        <button
          onClick={isOn ? onStop : onStart}
          disabled={connecting}
          className={`voice-btn${active ? ' voice-btn--active' : ''}${connecting ? ' voice-btn--connecting' : ''}`}
          aria-label={isOn ? 'End call' : 'Start voice call'}
        >
          {active ? <StopIcon /> : <MicIcon />}
        </button>
      </div>
    </div>
  );
};
