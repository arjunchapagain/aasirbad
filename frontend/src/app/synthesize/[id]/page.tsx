'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { toast } from 'sonner';
import {
  Mic,
  PlayCircle,
  PauseCircle,
  Loader2,
  ArrowLeft,
  Settings2,
} from 'lucide-react';

import { synthesis, voiceProfiles } from '@/lib/api';
import type { VoiceProfile, SynthesisResponse, SynthesisRequest } from '@/types';

const PRESETS = [
  { value: 'ultra_fast', label: 'Ultra Fast', desc: 'Fastest, lower quality' },
  { value: 'fast', label: 'Fast', desc: 'Good balance of speed and quality' },
  { value: 'standard', label: 'Standard', desc: 'High quality, slower' },
  { value: 'high_quality', label: 'High Quality', desc: 'Best quality, slowest' },
] as const;

export default function SynthesizePage() {
  const params = useParams();
  const router = useRouter();
  const profileId = params.id as string;

  const [profile, setProfile] = useState<VoiceProfile | null>(null);
  const [text, setText] = useState('');
  const [preset, setPreset] = useState<SynthesisRequest['preset']>('fast');
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<SynthesisResponse | null>(null);
  const [playing, setPlaying] = useState(false);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);
  const [history, setHistory] = useState<SynthesisResponse[]>([]);

  useEffect(() => {
    async function loadProfile() {
      try {
        const data = await voiceProfiles.get(profileId);
        setProfile(data);
      } catch {
        router.push('/dashboard');
      }
    }
    loadProfile();
  }, [profileId, router]);

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();

    if (!text.trim()) {
      toast.error('Please enter some text');
      return;
    }

    setGenerating(true);
    setResult(null);

    try {
      const response = await synthesis.generate({
        text: text.trim(),
        voice_profile_id: profileId,
        preset,
      });

      setResult(response);
      setHistory((prev) => [response, ...prev]);
      toast.success(`Generated ${response.duration_seconds}s of audio`);

      // Auto-play
      const audio = new Audio(response.audio_url);
      audio.onended = () => setPlaying(false);
      setAudioElement(audio);
      audio.play();
      setPlaying(true);
    } catch (err: any) {
      toast.error(err.detail || 'Synthesis failed');
    } finally {
      setGenerating(false);
    }
  }

  function togglePlayback() {
    if (!audioElement) return;

    if (playing) {
      audioElement.pause();
      setPlaying(false);
    } else {
      audioElement.play();
      setPlaying(true);
    }
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => router.push('/dashboard')}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
              <span className="text-white text-sm font-bold">ॐ</span>
            </div>
            <span className="font-bold text-gray-900">आसिर्बाद</span>
          </div>
          {profile && (
            <span className="text-sm text-gray-500 ml-auto">
              Voice: <span className="font-medium text-gray-900">{profile.name}</span>
            </span>
          )}
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Input Section */}
          <div className="lg:col-span-2">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">
              Generate Speech
            </h1>

            <form onSubmit={handleGenerate}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Enter text to speak
                </label>
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 outline-none transition-all resize-none"
                  rows={6}
                  placeholder="Type or paste the text you want to hear in the cloned voice..."
                  maxLength={5000}
                />
                <div className="flex justify-end mt-1">
                  <span className="text-xs text-gray-400">
                    {text.length}/5000 characters
                  </span>
                </div>
              </div>

              {/* Preset Selection */}
              <div className="mb-6">
                <label className="flex items-center gap-1.5 text-sm font-medium text-gray-700 mb-2">
                  <Settings2 className="w-4 h-4" />
                  Quality Preset
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {PRESETS.map((p) => (
                    <button
                      key={p.value}
                      type="button"
                      onClick={() => setPreset(p.value)}
                      className={`p-3 rounded-lg border text-left transition-all ${
                        preset === p.value
                          ? 'border-brand-500 bg-brand-50 ring-2 ring-brand-500/20'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <span className="text-sm font-medium text-gray-900 block">
                        {p.label}
                      </span>
                      <span className="text-xs text-gray-500">{p.desc}</span>
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={generating || !text.trim()}
                className="w-full bg-brand-600 text-white py-3 rounded-xl hover:bg-brand-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {generating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <PlayCircle className="w-5 h-5" />
                    Generate Speech
                  </>
                )}
              </button>
            </form>

            {/* Result Playback */}
            {result && (
              <div className="mt-6 bg-white rounded-xl border border-gray-100 p-6">
                <div className="flex items-center gap-4">
                  <button
                    onClick={togglePlayback}
                    className="w-14 h-14 rounded-full bg-brand-600 flex items-center justify-center hover:bg-brand-700 transition-colors shadow-lg shadow-brand-600/20"
                  >
                    {playing ? (
                      <PauseCircle className="w-7 h-7 text-white" />
                    ) : (
                      <PlayCircle className="w-7 h-7 text-white" />
                    )}
                  </button>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900 font-medium line-clamp-2">
                      {result.text}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {result.duration_seconds}s &bull; {preset}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* History Sidebar */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">
              Generation History
            </h3>
            {history.length === 0 ? (
              <p className="text-sm text-gray-400">No generations yet</p>
            ) : (
              <div className="space-y-3">
                {history.map((item, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      const audio = new Audio(item.audio_url);
                      audio.onended = () => setPlaying(false);
                      setAudioElement(audio);
                      audio.play();
                      setPlaying(true);
                      setResult(item);
                    }}
                    className="w-full text-left bg-white rounded-lg border border-gray-100 p-3 hover:shadow-sm transition-shadow"
                  >
                    <p className="text-sm text-gray-900 line-clamp-2">
                      {item.text}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      {item.duration_seconds}s
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
