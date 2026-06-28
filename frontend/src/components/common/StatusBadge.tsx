import type { SourceStatus } from '../../types/source';

interface Props {
  status: SourceStatus;
}

export const StatusBadge = ({ status }: Props) => (
  <span className={`badge badge--${status}`}>
    {status}
  </span>
);
