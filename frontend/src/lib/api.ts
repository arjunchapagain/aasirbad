/**
 * API client for Aasirbad backend.
 *
 * Features:
 * - Automatic token refresh on 401 (iOS-ready seamless re-auth)
 * - Request ID tracing via X-Request-ID header
 * - Structured error responses with request_id for support
 * - Prevents concurrent refresh token races
 */

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ── Error Class ─────────────────────────────────────────────────────────────

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
    public requestId?: string,
  ) {
    super(detail);
    this.name = 'ApiError';
  }
}

// ── Token Management ────────────────────────────────────────────────────────

const TokenStore = {
  getAccess: () =>
    typeof window !== 'undefined'
      ? localStorage.getItem('access_token')
      : null,
  getRefresh: () =>
    typeof window !== 'undefined'
      ? localStorage.getItem('refresh_token')
      : null,
  set: (access: string, refresh: string) => {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  },
  clear: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

// Prevent concurrent refresh races (critical for iOS parallel requests)
let refreshPromise: Promise<boolean> | null = null;

async function refreshTokens(): Promise<boolean> {
  const refreshToken = TokenStore.getRefresh();
  if (!refreshToken) return false;

  try {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      TokenStore.clear();
      return false;
    }

    const data = await response.json();
    TokenStore.set(data.access_token, data.refresh_token);
    return true;
  } catch {
    TokenStore.clear();
    return false;
  }
}

// ── Core Request Function ───────────────────────────────────────────────────

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  _isRetry = false,
): Promise<T> {
  const token = TokenStore.getAccess();

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

  // ── Auto-refresh on 401 (iOS seamless re-auth) ──────────────────────────
  if (response.status === 401 && !_isRetry && !endpoint.includes('/auth/')) {
    // Coalesce concurrent refreshes into a single request
    if (!refreshPromise) {
      refreshPromise = refreshTokens().finally(() => {
        refreshPromise = null;
      });
    }

    const refreshed = await refreshPromise;
    if (refreshed) {
      return request<T>(endpoint, options, true);
    }

    // Refresh failed — clear tokens and redirect to login
    TokenStore.clear();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(
      response.status,
      error.detail || 'Request failed',
      error.request_id,
    );
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

  login: async (email: string, password: string) => {
    const tokens = await request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    TokenStore.set(tokens.access_token, tokens.refresh_token);
    return tokens;
  },

  refresh: (refresh_token: string) =>
    request<TokenResponse>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token }),
    }),

  logout: async () => {
    try {
      await request<void>('/auth/logout', { method: 'POST' });
    } finally {
      TokenStore.clear();
    }
  },

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
