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
  Loader2,
  Volume2,
  Lightbulb,
  Info,
} from 'lucide-react';

import { recording } from '@/lib/api';
import { useAudioRecorder } from '@/hooks/useAudioRecorder';
import { formatDuration } from '@/lib/audio-utils';
import type { RecordingSession } from '@/types';

interface CompletedRecording {
  index: number;
  duration: number;
  status: 'completed' | 'rejected';
  message?: string;
}

export default function RecordPage() {
  const params = useParams();
  const token = params.token as string;

  const [session, setSession] = useState<RecordingSession | null>(null);
  const [recordings, setRecordings] = useState<CompletedRecording[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);

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

  // The next recording number (0-based for API, display as 1-based)
  const nextIndex = session ? session.completed_recordings + recordings.length : 0;
  const totalCompleted = session ? session.completed_recordings + recordings.filter(r => r.status === 'completed').length : 0;

  // Load session
  useEffect(() => {
    async function loadSession() {
      try {
        const data = await recording.getSession(token);
        setSession(data);
      } catch (err: any) {
        setError(err.detail || 'लिङ्क मान्य छैन');
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

      try {
        const result = await recording.upload(token, nextIndex, audioBlob);

        const newRecording: CompletedRecording = {
          index: nextIndex,
          duration: duration,
          status: result.status === 'rejected' ? 'rejected' : 'completed',
          message: result.message,
        };

        setRecordings((prev) => [...prev, newRecording]);

        if (result.status === 'rejected') {
          toast.error(result.message || 'रेकर्डिङ अस्वीकार भयो');
        } else {
          toast.success('रेकर्डिङ सेभ भयो!');
        }
      } catch (err: any) {
        toast.error(err.detail || 'अपलोड असफल भयो');
      } finally {
        setUploading(false);
      }
    } else {
      // Start recording
      await startRecording();
    }
  }, [isRecording, stopRecording, startRecording, token, nextIndex, duration]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-8 h-8 text-brand-600 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 bg-gray-50">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h1 className="text-xl font-bold text-gray-900 mb-2">लिङ्क मान्य छैन</h1>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  const minReached = session ? totalCompleted >= session.min_required : false;
  const maxReached = session ? nextIndex >= session.max_recordings : false;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-100">
        <div className="max-w-2xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
                <span className="text-white text-sm font-bold">ॐ</span>
              </div>
              <span className="font-bold text-gray-900">आसिर्बाद</span>
            </div>
            <div className="text-sm text-gray-600">
              <span className="font-medium text-gray-900">{session?.profile_name}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-8">
        {/* Title */}
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            भ्वाइस रेकर्डिङ
          </h1>
          <p className="text-gray-500 text-sm">
            कृपया नेपालीमा बोलेर आफ्नो आवाज रेकर्ड गर्नुहोस्
          </p>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>
              {totalCompleted} रेकर्डिङ पूरा
              {minReached && (
                <span className="text-green-600 ml-2">✓ न्यूनतम पुग्यो</span>
              )}
            </span>
            <span>कम्तिमा {session?.min_required} चाहिन्छ</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-brand-600 h-2.5 rounded-full transition-all duration-500"
              style={{
                width: `${Math.min(100, (totalCompleted / (session?.min_required || 1)) * 100)}%`,
              }}
            />
          </div>
        </div>

        {/* Tips */}
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-2">
            <Info className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-semibold text-blue-900 mb-2">सुझावहरू</h3>
              <ul className="space-y-1">
                {session?.tips.map((tip, i) => (
                  <li key={i} className="text-sm text-blue-800">
                    • {tip.text_ne}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Recording Card */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8 mb-6">
          {maxReached ? (
            <div className="text-center py-4">
              <CheckCircle2 className="w-12 h-12 text-green-500 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                अधिकतम रेकर्डिङ पूरा भयो!
              </h3>
              <p className="text-gray-500 text-sm">
                तपाईंले अधिकतम {session?.max_recordings} रेकर्डिङ गर्नुभयो।
              </p>
            </div>
          ) : (
            <>
              {/* Recording number */}
              <div className="text-center mb-4">
                <span className="text-sm font-medium text-brand-600 bg-brand-50 px-3 py-1 rounded-full">
                  रेकर्डिङ #{nextIndex + 1}
                </span>
              </div>

              {/* Instruction */}
              <p className="text-center text-gray-700 mb-6 text-lg">
                कृपया कुनै पनि कुरा नेपालीमा बोल्नुहोस्
              </p>

              {/* Audio Level Visualizer */}
              <div className="flex items-center justify-center gap-1 h-16 mb-6">
                {isRecording ? (
                  Array.from({ length: 24 }).map((_, i) => (
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
                    <span className="text-sm">रेकर्ड बटन थिच्नुहोस्</span>
                  </div>
                )}
              </div>

              {/* Recording Duration */}
              {isRecording && (
                <div className="text-center mb-4">
                  <span className="text-3xl font-mono font-medium text-red-500">
                    {formatDuration(duration)}
                  </span>
                </div>
              )}

              {/* Record Button */}
              <div className="flex justify-center">
                <button
                  onClick={handleRecord}
                  disabled={!isReady || uploading}
                  className={`w-24 h-24 rounded-full flex items-center justify-center transition-all shadow-lg ${
                    isRecording
                      ? 'bg-red-500 hover:bg-red-600 shadow-red-500/30 animate-pulse'
                      : uploading
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-brand-600 hover:bg-brand-700 shadow-brand-600/30 hover:scale-105'
                  }`}
                >
                  {uploading ? (
                    <Loader2 className="w-10 h-10 text-white animate-spin" />
                  ) : isRecording ? (
                    <Square className="w-10 h-10 text-white" />
                  ) : (
                    <Mic className="w-10 h-10 text-white" />
                  )}
                </button>
              </div>

              {/* Status message */}
              <p className="text-center text-sm text-gray-500 mt-4">
                {!isReady
                  ? 'माइक्रोफोनको अनुमति दिनुहोस्'
                  : uploading
                    ? 'अपलोड हुँदैछ...'
                    : isRecording
                      ? 'रोक्न बटन थिच्नुहोस्'
                      : 'रेकर्ड सुरु गर्न बटन थिच्नुहोस्'}
              </p>
            </>
          )}

          {/* Recorder errors */}
          {recorderError && (
            <div className="mt-4 p-3 bg-red-50 border border-red-100 rounded-lg text-sm text-red-700 flex items-start gap-2">
              <MicOff className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>{recorderError}</span>
            </div>
          )}
        </div>

        {/* Optional Suggestions */}
        <div className="bg-white rounded-xl border border-gray-100 mb-6">
          <button
            onClick={() => setShowSuggestions(!showSuggestions)}
            className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors rounded-xl"
          >
            <div className="flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-amber-500" />
              <span className="text-sm font-medium text-gray-700">
                के बोल्ने? — विचारहरू
              </span>
            </div>
            <span className="text-xs text-gray-400">
              {showSuggestions ? 'लुकाउनुहोस्' : 'हेर्नुहोस्'}
            </span>
          </button>
          {showSuggestions && (
            <div className="px-4 pb-4 space-y-2">
              {session?.suggestions.map((s, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 p-2 rounded-lg bg-amber-50"
                >
                  <span className="text-amber-600 text-sm mt-0.5">•</span>
                  <div>
                    <p className="text-sm text-gray-800">{s.text_ne}</p>
                    <p className="text-xs text-gray-400">{s.text_en}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recording History */}
        {recordings.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-100 divide-y divide-gray-50">
            <div className="px-4 py-3">
              <h3 className="text-sm font-semibold text-gray-900">
                यस सत्रका रेकर्डिङहरू
              </h3>
            </div>
            {[...recordings].reverse().map((rec) => (
              <div
                key={rec.index}
                className="px-4 py-3 flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  {rec.status === 'completed' ? (
                    <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                  )}
                  <span className="text-sm text-gray-900">
                    रेकर्डिङ #{rec.index + 1}
                  </span>
                </div>
                <span className="text-xs text-gray-400">
                  {formatDuration(rec.duration)}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Minimum Reached Message */}
        {minReached && !maxReached && (
          <div className="mt-6 bg-green-50 border border-green-200 rounded-xl p-6 text-center">
            <CheckCircle2 className="w-10 h-10 text-green-500 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-green-900 mb-1">
              न्यूनतम रेकर्डिङ पुग्यो!
            </h3>
            <p className="text-green-700 text-sm">
              अझ राम्रो गुणस्तरको लागि थप रेकर्डिङ गर्न सक्नुहुन्छ।
              <br />
              यो पेज बन्द गर्न सक्नुहुन्छ — भ्वाइस ट्रेनिङ सुरु गर्न सकिन्छ।
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
