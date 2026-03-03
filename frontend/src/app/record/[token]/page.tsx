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
  const [permissionRequested, setPermissionRequested] = useState(false);

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

  // Handle mic permission request
  const handlePermissionRequest = useCallback(async () => {
    setPermissionRequested(true);
    await requestPermission();
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

  // Show microphone permission request screen if not ready and permission hasn't been requested yet
  if (!isReady && !permissionRequested) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center mx-auto mb-4">
              <Mic className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">माइक्रोफोन अनुमति चाहिन्छ</h1>
            <p className="text-gray-600 text-sm">
              भ्वाइस रेकर्डिङ गर्न माइक्रोफोनको अनुमति दिनुपर्छ
            </p>
          </div>

          {/* Information Card */}
          <div className="bg-white rounded-2xl p-6 shadow-lg mb-6">
            <div className="space-y-4">
              <div className="flex gap-3">
                <div className="flex-shrink-0">
                  <Mic className="w-5 h-5 text-blue-600 mt-0.5" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 text-sm">
                    माइक्रोफोन अनुमति किन चाहिन्छ?
                  </h3>
                  <p className="text-gray-500 text-xs mt-1">
                    तपाईंको आवाज रेकर्ड गर्न र आवाज प्रशिक्षण मडेल बनाउन माइक्रोफोन अनुमति आवश्यक छ।
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex-shrink-0">
                  <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 text-sm">
                    यो सुरक्षित छ
                  </h3>
                  <p className="text-gray-500 text-xs mt-1">
                    आपको रेकर्डिङ केवल भ्वाइस प्रशिक्षणको लागि प्रयोग गरिन्छ।
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex-shrink-0">
                  <Info className="w-5 h-5 text-green-600 mt-0.5" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 text-sm">
                    सरल प्रक्रिया
                  </h3>
                  <p className="text-gray-500 text-xs mt-1">
                    तल रहेको बटन थिच्नुहोस् र ब्राउजरले अनुमति सोध्नेछ।
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Permission Button */}
          <button
            onClick={handlePermissionRequest}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-4 px-6 rounded-xl transition-all shadow-lg hover:shadow-xl active:scale-95"
          >
            <div className="flex items-center justify-center gap-2">
              <Mic className="w-5 h-5" />
              माइक्रोफोन अनुमति दिनुहोस्
            </div>
          </button>

          {/* Fallback message */}
          <p className="text-center text-xs text-gray-500 mt-4">
            ब्राउजरमा अनुमति संवाद देखा पर्नेछ। कृपया &quot;अनुमति दिनुहोस्&quot; वा &quot;Allow&quot; विकल्प चयन गर्नुहोस्।
          </p>

          {/* Browser-specific instructions */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-600 font-semibold mb-3">यदि अनुमति संवाद न देखिए:</p>
            <div className="space-y-2 text-xs text-gray-600">
              <details className="group">
                <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
                  Chrome / Edge मा
                </summary>
                <div className="mt-2 ml-2 space-y-1 text-xs">
                  <p>1. ब्राउजरको माथिपट्टि लकमा क्लिक गर्नुहोस्</p>
                  <p>2. &quot;साइट सेटिङहरू&quot; चयन गर्नुहोस्</p>
                  <p>3. माइक्रोफोन अनुमति दिनुहोस्</p>
                </div>
              </details>
              <details className="group">
                <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
                  Firefox मा
                </summary>
                <div className="mt-2 ml-2 space-y-1 text-xs">
                  <p>1. ब्राउजार मेनु (☰) खोल्नुहोस्</p>
                  <p>2. Settings &gt; Privacy &gt; Permissions</p>
                  <p>3. Microphone खोज्नुहोस् र &quot;Allow&quot; गर्नुहोस्</p>
                </div>
              </details>
              <details className="group">
                <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
                  Safari (iPhone/iPad) मा
                </summary>
                <div className="mt-2 ml-2 space-y-1 text-xs">
                  <p>1. Settings &gt; [App नाम] &gt; Microphone</p>
                  <p>2. &quot;Allow&quot; चयन गर्नुहोस्</p>
                </div>
              </details>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show error screen if permission was requested but failed
  if (!isReady && permissionRequested && recorderError) {
    return (
      <div className="min-h-screen bg-red-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full">
          <div className="text-center">
            <MicOff className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">माइक्रोफोन अनुमति दिन सकेन</h1>
            <p className="text-gray-600 text-sm mb-6">{recorderError}</p>

            <button
              onClick={handlePermissionRequest}
              className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-xl transition-all mb-3"
            >
              अनुमति पुनः दिने प्रयास गर्नुहोस्
            </button>

            <a
              href="/"
              className="block text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              गृह पृष्ठमा फर्कनुहोस्
            </a>
          </div>
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
              <div className="text-center mt-4">
                {isReady ? (
                  <p className="text-sm text-gray-500">
                    {uploading
                      ? 'अपलोड हुँदैछ...'
                      : isRecording
                        ? 'रोक्न बटन थिच्नुहोस्'
                        : 'रेकर्ड सुरु गर्न बटन थिच्नुहोस्'}
                  </p>
                ) : (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <p className="text-xs text-blue-700 font-medium">
                      ✓ माइक्रोफोन तयार छ
                    </p>
                  </div>
                )}
              </div>
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
