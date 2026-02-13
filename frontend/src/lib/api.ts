/**
 * API client for VoiceForge backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = 'ApiError';
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const token =
    typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  const headers: HeadersInit = {
    ...(options.headers || {}),
  };

  // Don't set Content-Type for FormData (browser sets boundary automatically)
  if (!(options.body instanceof FormData)) {
    (headers as Record<string, string>)['Content-Type'] = 'application/json';
  }

  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || 'Request failed');
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

// ── Auth ────────────────────────────────────────────────────────────────────

import type {
  RecordingLinkResponse,
  RecordingSession,
  RecordingUploadResponse,
  SynthesisRequest,
  SynthesisResponse,
  TokenResponse,
  User,
  VoiceProfile,
  VoiceProfileListResponse,
} from '@/types';

export const auth = {
  register: (data: { email: string; password: string; full_name: string }) =>
    request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (email: string, password: string) =>
    request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  refresh: (refresh_token: string) =>
    request<TokenResponse>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token }),
    }),

  me: () => request<User>('/auth/me'),
};

// ── Voice Profiles ──────────────────────────────────────────────────────────

export const voiceProfiles = {
  create: (data: { name: string; description?: string }) =>
    request<VoiceProfile>('/voice-profiles', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  list: (page = 1, pageSize = 20) =>
    request<VoiceProfileListResponse>(
      `/voice-profiles?page=${page}&page_size=${pageSize}`,
    ),

  get: (id: string) => request<VoiceProfile>(`/voice-profiles/${id}`),

  delete: (id: string) =>
    request<void>(`/voice-profiles/${id}`, { method: 'DELETE' }),

  getRecordingLink: (id: string) =>
    request<RecordingLinkResponse>(`/voice-profiles/${id}/link`),

  triggerTraining: (id: string) =>
    request<{ job_id: string; status: string; message: string }>(
      `/voice-profiles/${id}/train`,
      { method: 'POST' },
    ),
};

// ── Public Recording ────────────────────────────────────────────────────────

export const recording = {
  getSession: (token: string) =>
    request<RecordingSession>(`/voice-profiles/record/${token}`),

  upload: (token: string, promptIndex: number, audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('prompt_index', promptIndex.toString());
    formData.append('audio_file', audioBlob, 'recording.wav');

    return request<RecordingUploadResponse>(`/recordings/${token}/upload`, {
      method: 'POST',
      body: formData,
    });
  },
};

// ── Synthesis ───────────────────────────────────────────────────────────────

export const synthesis = {
  generate: (data: SynthesisRequest) =>
    request<SynthesisResponse>('/synthesis/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

export { ApiError };
