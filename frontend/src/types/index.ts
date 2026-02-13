/**
 * TypeScript type definitions for Aasirbad.
 */

// ── User Types ──────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// ── Voice Profile Types ─────────────────────────────────────────────────────

export type ProfileStatus =
  | 'pending'
  | 'recording'
  | 'processing'
  | 'training'
  | 'ready'
  | 'failed'
  | 'archived';

export interface VoiceProfile {
  id: string;
  name: string;
  description: string | null;
  status: ProfileStatus;
  recording_token: string;
  total_recordings: number;
  total_duration_seconds: number;
  training_progress: number;
  voice_similarity_score: number | null;
  training_started_at: string | null;
  training_completed_at: string | null;
  training_error: string | null;
  created_at: string;
  updated_at: string;
}

export interface VoiceProfileListResponse {
  items: VoiceProfile[];
  total: number;
  page: number;
  page_size: number;
}

// ── Recording Types ─────────────────────────────────────────────────────────

export interface RecordingTip {
  text_ne: string;
  text_en: string;
}

export interface RecordingSuggestion {
  text_ne: string;
  text_en: string;
}

export interface RecordingSession {
  profile_name: string;
  tips: RecordingTip[];
  suggestions: RecordingSuggestion[];
  completed_recordings: number;
  max_recordings: number;
  min_required: number;
}

export type RecordingStatus =
  | 'uploaded'
  | 'processing'
  | 'processed'
  | 'rejected'
  | 'failed';

export interface RecordingUploadResponse {
  recording_id: string;
  status: RecordingStatus;
  quality_metrics: {
    snr_db: number;
    rms_level: number;
    clipping_detected: boolean;
    silence_ratio: number;
  } | null;
  message: string;
}

// ── Synthesis Types ─────────────────────────────────────────────────────────

export interface SynthesisRequest {
  text: string;
  voice_profile_id: string;
  speed?: number;
  preset?: 'ultra_fast' | 'fast' | 'standard' | 'high_quality';
}

export interface SynthesisResponse {
  audio_url: string;
  duration_seconds: number;
  text: string;
  voice_profile_id: string;
}

// ── Training Status (WebSocket) ─────────────────────────────────────────────

export interface TrainingStatus {
  profile_id: string;
  progress: number;
  step: string;
  status: 'training' | 'ready' | 'failed';
}

// ── Recording Link ──────────────────────────────────────────────────────────

export interface RecordingLinkResponse {
  recording_url: string;
  token: string;
  profile_name: string;
  expires_at: string | null;
}
