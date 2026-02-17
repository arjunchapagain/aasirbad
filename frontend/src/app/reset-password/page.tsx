'use client';

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { toast } from 'sonner';
import { Eye, EyeOff, CheckCircle } from 'lucide-react';

import { auth } from '@/lib/api';

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token') || '';

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      toast.error('पासवर्ड मेल खाएन');
      return;
    }

    if (password.length < 8) {
      toast.error('पासवर्ड कम्तिमा ८ अक्षर हुनुपर्छ');
      return;
    }

    setLoading(true);

    try {
      await auth.resetPassword(token, password);
      setSuccess(true);
      toast.success('पासवर्ड सफलतापूर्वक रिसेट भयो!');
      setTimeout(() => router.push('/login'), 3000);
    } catch (err: any) {
      toast.error(err.detail || 'रिसेट लिंक अमान्य वा म्याद सकिएको छ');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center">
        <h2 className="text-lg font-semibold text-red-600 mb-2">अमान्य लिंक</h2>
        <p className="text-gray-600 text-sm mb-4">
          यो रिसेट लिंक अमान्य छ। कृपया फेरि प्रयास गर्नुहोस्।
        </p>
        <Link
          href="/forgot-password"
          className="text-brand-600 hover:text-brand-700 font-medium text-sm"
        >
          नयाँ रिसेट लिंक लिनुहोस्
        </Link>
      </div>
    );
  }

  if (success) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center">
        <div className="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-7 h-7 text-green-600" />
        </div>
        <h2 className="text-lg font-semibold text-gray-900 mb-2">पासवर्ड रिसेट भयो!</h2>
        <p className="text-gray-600 text-sm">
          लगइन पेजमा रिडाइरेक्ट हुँदैछ...
        </p>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 space-y-5"
    >
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          नयाँ पासवर्ड
        </label>
        <div className="relative">
          <input
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            className="w-full px-4 py-2.5 rounded-lg border border-gray-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 outline-none transition-all pr-10"
            placeholder="कम्तिमा ८ अक्षर"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          पासवर्ड पुष्टि गर्नुहोस्
        </label>
        <input
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          minLength={8}
          className="w-full px-4 py-2.5 rounded-lg border border-gray-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 outline-none transition-all"
          placeholder="पासवर्ड फेरि हाल्नुहोस्"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-brand-600 text-white py-2.5 rounded-lg hover:bg-brand-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'रिसेट गर्दै...' : 'पासवर्ड रिसेट गर्नुहोस्'}
      </button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2.5 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-md shadow-amber-500/20">
              <span className="text-white text-xl font-bold">ॐ</span>
            </div>
            <div className="flex flex-col leading-tight">
              <span className="text-2xl font-bold text-gray-900">आसिर्बाद</span>
              <span className="text-[10px] text-amber-700 font-medium -mt-0.5">AASIRBAD</span>
            </div>
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">नयाँ पासवर्ड सेट गर्नुहोस्</h1>
        </div>

        <Suspense fallback={<div className="text-center text-gray-500">Loading...</div>}>
          <ResetPasswordForm />
        </Suspense>
      </div>
    </div>
  );
}
