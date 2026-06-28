export type SourceStatus = 'ready' | 'failed';
export type SourceType = 'resume' | 'url';

export interface Source {
  id: string;
  type: SourceType;
  label: string;
  url?: string;
  status: SourceStatus;
  error?: string;
  chunk_count: number;
  indexed_at?: string;
  created_at: string;
}
