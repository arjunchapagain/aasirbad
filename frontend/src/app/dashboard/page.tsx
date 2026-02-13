'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import {
  Mic,
  Plus,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Link as LinkIcon,
  Trash2,
  PlayCircle,
  Wand2,
  LogOut,
} from 'lucide-react';

import { auth, voiceProfiles } from '@/lib/api';
import type { User, VoiceProfile, ProfileStatus } from '@/types';

const STATUS_CONFIG: Record<
  ProfileStatus,
  { label: string; color: string; icon: React.ReactNode }
> = {
  pending: { label: 'Pending', color: 'bg-gray-100 text-gray-700', icon: <Clock className="w-3.5 h-3.5" /> },
  recording: { label: 'Recording', color: 'bg-blue-100 text-blue-700', icon: <Mic className="w-3.5 h-3.5" /> },
  processing: { label: 'Processing', color: 'bg-yellow-100 text-yellow-700', icon: <Loader2 className="w-3.5 h-3.5 animate-spin" /> },
  training: { label: 'Training', color: 'bg-purple-100 text-purple-700', icon: <Loader2 className="w-3.5 h-3.5 animate-spin" /> },
  ready: { label: 'Ready', color: 'bg-green-100 text-green-700', icon: <CheckCircle2 className="w-3.5 h-3.5" /> },
  failed: { label: 'Failed', color: 'bg-red-100 text-red-700', icon: <AlertCircle className="w-3.5 h-3.5" /> },
  archived: { label: 'Archived', color: 'bg-gray-100 text-gray-500', icon: <Clock className="w-3.5 h-3.5" /> },
};

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [profiles, setProfiles] = useState<VoiceProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDescription, setNewDescription] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [userData, profilesData] = await Promise.all([
        auth.me(),
        voiceProfiles.list(),
      ]);
      setUser(userData);
      setProfiles(profilesData.items);
    } catch {
      router.push('/login');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    try {
      const profile = await voiceProfiles.create({
        name: newName,
        description: newDescription || undefined,
      });
      setProfiles((prev) => [profile, ...prev]);
      setShowCreateModal(false);
      setNewName('');
      setNewDescription('');
      toast.success('Voice profile created!');
    } catch (err: any) {
      toast.error(err.detail || 'Failed to create profile');
    } finally {
      setCreating(false);
    }
  }

  async function handleCopyLink(profileId: string) {
    try {
      const link = await voiceProfiles.getRecordingLink(profileId);
      await navigator.clipboard.writeText(link.recording_url);
      toast.success('Recording link copied to clipboard!');
    } catch (err: any) {
      toast.error(err.detail || 'Failed to get link');
    }
  }

  async function handleTrain(profileId: string) {
    try {
      const result = await voiceProfiles.triggerTraining(profileId);
      toast.success(result.message);
      loadData();
    } catch (err: any) {
      toast.error(err.detail || 'Failed to start training');
    }
  }

  async function handleDelete(profileId: string) {
    if (!confirm('Are you sure? This will delete all recordings and the trained model.')) return;
    try {
      await voiceProfiles.delete(profileId);
      setProfiles((prev) => prev.filter((p) => p.id !== profileId));
      toast.success('Voice profile deleted');
    } catch (err: any) {
      toast.error(err.detail || 'Failed to delete');
    }
  }

  async function handleLogout() {
    await auth.logout();
    router.push('/login');
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-brand-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
              <span className="text-white text-sm font-bold">ॐ</span>
            </div>
            <span className="text-lg font-bold text-gray-900">आसिर्बाद</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.full_name}</span>
            <button
              onClick={handleLogout}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Voice Profiles</h1>
            <p className="text-gray-600 mt-1">
              Manage your cloned voices
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 bg-brand-600 text-white px-5 py-2.5 rounded-lg hover:bg-brand-700 transition-colors font-medium"
          >
            <Plus className="w-4 h-4" />
            New Voice
          </button>
        </div>

        {/* Profiles Grid */}
        {profiles.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-gray-100">
            <Mic className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No voice profiles yet
            </h3>
            <p className="text-gray-600 mb-6">
              Create your first voice profile to get started
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center gap-2 bg-brand-600 text-white px-5 py-2.5 rounded-lg hover:bg-brand-700 transition-colors font-medium"
            >
              <Plus className="w-4 h-4" />
              Create Voice Profile
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {profiles.map((profile) => {
              const statusConfig = STATUS_CONFIG[profile.status];
              return (
                <div
                  key={profile.id}
                  className="bg-white rounded-xl border border-gray-100 p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-gray-900">{profile.name}</h3>
                      {profile.description && (
                        <p className="text-sm text-gray-500 mt-0.5">{profile.description}</p>
                      )}
                    </div>
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${statusConfig.color}`}
                    >
                      {statusConfig.icon}
                      {statusConfig.label}
                    </span>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                    <span>{profile.total_recordings} recordings</span>
                    <span>{Math.round(profile.total_duration_seconds)}s audio</span>
                  </div>

                  {/* Training Progress */}
                  {(profile.status === 'training' || profile.status === 'processing') && (
                    <div className="mb-4">
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                        <span>Training progress</span>
                        <span>{Math.round(profile.training_progress * 100)}%</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2">
                        <div
                          className="bg-brand-600 h-2 rounded-full progress-bar"
                          style={{ width: `${profile.training_progress * 100}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex items-center gap-2 pt-2 border-t border-gray-50">
                    {(profile.status === 'pending' || profile.status === 'recording') && (
                      <>
                        <button
                          onClick={() => handleCopyLink(profile.id)}
                          className="flex items-center gap-1.5 text-sm text-brand-600 hover:text-brand-700 font-medium"
                        >
                          <LinkIcon className="w-3.5 h-3.5" />
                          Copy Link
                        </button>
                        {profile.total_recordings >= 5 && (
                          <button
                            onClick={() => handleTrain(profile.id)}
                            className="flex items-center gap-1.5 text-sm text-purple-600 hover:text-purple-700 font-medium ml-auto"
                          >
                            <Wand2 className="w-3.5 h-3.5" />
                            Train
                          </button>
                        )}
                      </>
                    )}

                    {profile.status === 'ready' && (
                      <Link
                        href={`/synthesize/${profile.id}`}
                        className="flex items-center gap-1.5 text-sm text-green-600 hover:text-green-700 font-medium"
                      >
                        <PlayCircle className="w-3.5 h-3.5" />
                        Synthesize
                      </Link>
                    )}

                    <button
                      onClick={() => handleDelete(profile.id)}
                      className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-red-500 ml-auto transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-2xl p-8 w-full max-w-md shadow-xl">
            <h2 className="text-xl font-bold text-gray-900 mb-6">
              Create Voice Profile
            </h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Voice Name *
                </label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  required
                  className="w-full px-4 py-2.5 rounded-lg border border-gray-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 outline-none transition-all"
                  placeholder="e.g., John's Voice, CEO Narration"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Description
                </label>
                <textarea
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-lg border border-gray-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 outline-none transition-all"
                  rows={3}
                  placeholder="Optional description..."
                />
              </div>
              <div className="flex items-center gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 py-2.5 rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-50 transition-colors font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating || !newName.trim()}
                  className="flex-1 bg-brand-600 text-white py-2.5 rounded-lg hover:bg-brand-700 transition-colors font-medium disabled:opacity-50"
                >
                  {creating ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
