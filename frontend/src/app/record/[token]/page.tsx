'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { toast } from 'sonner';
import {
  Mic,
  MicOff,
  Square,
  CheckCircle2,
  AlertCircle,
  ChevronRight,
  ChevronLeft,
  Loader2,
  Volume2,
} from 'lucide-react';

import { recording } from '@/lib/api';
import { useAudioRecorder } from '@/hooks/useAudioRecorder';
import { formatDuration } from '@/lib/audio-utils';
import type { RecordingPrompt, RecordingSession } from '@/types';

type PromptStatus = 'pending' | 'recording' | 'uploading' | 'completed' | 'rejected' | 'error';

interface PromptState {
  prompt: RecordingPrompt;
  status: PromptStatus;
  message?: string;
}

export default function RecordPage() {
  const params = useParams();
  const token = params.token as string;

  const [session, setSession] = useState<RecordingSession | null>(null);
  const [promptStates, setPromptStates] = useState<PromptState[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const {
    isRecording,
    isReady,
    audioLevel,
    duration,
    startRecording,
    stopRecording,
    requestPermission,
    error: recorderError,
  } = useAudioRecorder();

  // Load session
  useEffect(() => {
    async function loadSession() {
      try {
        const data = await recording.getSession(token);
        setSession(data);
        setPromptStates(
          data.prompts.map((p) => ({
            prompt: p,
            status: 'pending' as PromptStatus,
          })),
        );
        // Skip already completed prompts
        setCurrentIndex(data.completed_recordings);
      } catch (err: any) {
        setError(err.detail || 'Invalid recording link');
      } finally {
        setLoading(false);
      }
    }
    loadSession();
  }, [token]);

  // Request mic permission on mount
  useEffect(() => {
    requestPermission();
  }, [requestPermission]);

  const handleRecord = useCallback(async () => {
    if (isRecording) {
      // Stop and upload
      const audioBlob = await stopRecording();
      if (!audioBlob) return;

      setUploading(true);
      setPromptStates((prev) =>
        prev.map((s, i) =>
          i === currentIndex ? { ...s, status: 'uploading' } : s,
        ),
      );

      try {
        const result = await recording.upload(
          token,
          currentIndex,
          audioBlob,
        );

        const newStatus: PromptStatus =
          result.status === 'rejected' ? 'rejected' : 'completed';

        setPromptStates((prev) =>
          prev.map((s, i) =>
            i === currentIndex
              ? { ...s, status: newStatus, message: result.message }
              : s,
          ),
        );

        if (result.status === 'rejected') {
          toast.error(result.message);
        } else {
          toast.success('Recording saved!');
          // Auto-advance
          if (currentIndex < promptStates.length - 1) {
            setTimeout(() => setCurrentIndex((i) => i + 1), 500);
          }
        }
      } catch (err: any) {
        setPromptStates((prev) =>
          prev.map((s, i) =>
            i === currentIndex
              ? { ...s, status: 'error', message: err.detail || 'Upload failed' }
              : s,
          ),
        );
        toast.error('Failed to upload recording');
      } finally {
        setUploading(false);
      }
    } else {
      // Start recording
      setPromptStates((prev) =>
        prev.map((s, i) =>
          i === currentIndex ? { ...s, status: 'recording' } : s,
        ),
      );
      await startRecording();
    }
  }, [isRecording, stopRecording, startRecording, token, currentIndex, promptStates.length]);

  const completedCount = promptStates.filter((s) => s.status === 'completed').length;
  const currentPrompt = promptStates[currentIndex];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-brand-600 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h1 className="text-xl font-bold text-gray-900 mb-2">Invalid Link</h1>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-100">
        <div className="max-w-3xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
                <Mic className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-gray-900">VoiceForge</span>
            </div>
            <div className="text-sm text-gray-600">
              Recording for <span className="font-medium text-gray-900">{session?.profile_name}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>
              {completedCount} of {session?.total_prompts} recordings
              {session && completedCount >= session.min_required && (
                <span className="text-green-600 ml-2">
                  (minimum reached!)
                </span>
              )}
            </span>
            <span>Prompt {currentIndex + 1}/{session?.total_prompts}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-brand-600 h-2 rounded-full progress-bar"
              style={{
                width: `${(completedCount / (session?.total_prompts || 1)) * 100}%`,
              }}
            />
          </div>
        </div>

        {/* Prompt Card */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8 mb-6">
          {/* Category badge */}
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xs font-medium text-brand-600 bg-brand-50 px-2.5 py-1 rounded-full">
              {currentPrompt?.prompt.category.replace('_', ' ')}
            </span>
            <span className="text-xs text-gray-400">
              ~{currentPrompt?.prompt.estimated_duration_seconds}s
            </span>
          </div>

          {/* Prompt text */}
          <blockquote className="text-xl sm:text-2xl font-medium text-gray-900 leading-relaxed mb-8">
            &ldquo;{currentPrompt?.prompt.text}&rdquo;
          </blockquote>

          {/* Audio Level Visualizer */}
          <div className="flex items-center justify-center gap-1 h-16 mb-6">
            {isRecording ? (
              Array.from({ length: 20 }).map((_, i) => (
                <div
                  key={i}
                  className="w-1.5 bg-brand-500 rounded-full transition-all duration-75"
                  style={{
                    height: `${Math.max(4, audioLevel * 64 * (1 + Math.sin(i * 0.5 + Date.now() / 200) * 0.3))}px`,
                    opacity: 0.4 + audioLevel * 0.6,
                  }}
                />
              ))
            ) : (
              <div className="flex items-center gap-2 text-gray-400">
                <Volume2 className="w-5 h-5" />
                <span className="text-sm">Read the text above aloud</span>
              </div>
            )}
          </div>

          {/* Recording Duration */}
          {isRecording && (
            <div className="text-center mb-4">
              <span className="text-2xl font-mono font-medium text-red-500">
                {formatDuration(duration)}
              </span>
            </div>
          )}

          {/* Record Button */}
          <div className="flex justify-center">
            <button
              onClick={handleRecord}
              disabled={!isReady || uploading}
              className={`w-20 h-20 rounded-full flex items-center justify-center transition-all shadow-lg ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 shadow-red-500/30 animate-pulse-slow'
                  : uploading
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-brand-600 hover:bg-brand-700 shadow-brand-600/30'
              }`}
            >
              {uploading ? (
                <Loader2 className="w-8 h-8 text-white animate-spin" />
              ) : isRecording ? (
                <Square className="w-8 h-8 text-white" />
              ) : (
                <Mic className="w-8 h-8 text-white" />
              )}
            </button>
          </div>

          {/* Status message */}
          <p className="text-center text-sm text-gray-500 mt-4">
            {!isReady
              ? 'Please allow microphone access'
              : uploading
                ? 'Uploading and analyzing...'
                : isRecording
                  ? 'Click to stop recording'
                  : 'Click to start recording'}
          </p>

          {/* Rejection / Error message */}
          {currentPrompt?.status === 'rejected' && (
            <div className="mt-4 p-3 bg-red-50 border border-red-100 rounded-lg text-sm text-red-700 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>{currentPrompt.message} - Please try again.</span>
            </div>
          )}

          {recorderError && (
            <div className="mt-4 p-3 bg-red-50 border border-red-100 rounded-lg text-sm text-red-700 flex items-start gap-2">
              <MicOff className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>{recorderError}</span>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
            disabled={currentIndex === 0 || isRecording}
            className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </button>
          <button
            onClick={() =>
              setCurrentIndex((i) => Math.min(promptStates.length - 1, i + 1))
            }
            disabled={currentIndex >= promptStates.length - 1 || isRecording}
            className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {/* Prompt List */}
        <div className="mt-8 bg-white rounded-xl border border-gray-100 divide-y divide-gray-50">
          <div className="px-4 py-3">
            <h3 className="text-sm font-semibold text-gray-900">All Prompts</h3>
          </div>
          {promptStates.map((state, index) => (
            <button
              key={index}
              onClick={() => !isRecording && setCurrentIndex(index)}
              className={`w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-gray-50 transition-colors ${
                index === currentIndex ? 'bg-brand-50' : ''
              }`}
            >
              {state.status === 'completed' ? (
                <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
              ) : state.status === 'rejected' ? (
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              ) : (
                <div
                  className={`w-5 h-5 rounded-full border-2 flex-shrink-0 ${
                    index === currentIndex
                      ? 'border-brand-500'
                      : 'border-gray-200'
                  }`}
                />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900 truncate">
                  {state.prompt.text}
                </p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {state.prompt.category.replace('_', ' ')}
                </p>
              </div>
            </button>
          ))}
        </div>

        {/* Completion Message */}
        {session && completedCount >= session.min_required && (
          <div className="mt-8 bg-green-50 border border-green-200 rounded-xl p-6 text-center">
            <CheckCircle2 className="w-10 h-10 text-green-500 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-green-900 mb-1">
              Minimum recordings reached!
            </h3>
            <p className="text-green-700 text-sm">
              You can continue recording more prompts for better voice quality,
              or close this page. The voice owner can now start training.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
