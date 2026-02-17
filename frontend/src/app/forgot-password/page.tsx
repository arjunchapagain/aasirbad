'use client';

import { useState } from 'react';
import Link from 'next/link';
import { toast } from 'sonner';
import { Mail, ArrowLeft } from 'lucide-react';

import { auth } from '@/lib/api';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await auth.forgotPassword(email);
      setSent(true);
      toast.success('रिसेट लिंक पठाइयो!');
    } catch {
      // Always show success to prevent email enumeration
      setSent(true);
    } finally {
      setLoading(false);
    }
  };

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
          <h1 className="text-2xl font-bold text-gray-900">पासवर्ड बिर्सनुभयो?</h1>
          <p className="text-gray-600 mt-1">आफ्नो इमेल हाल्नुहोस्, हामी रिसेट लिंक पठाउँछौं</p>
        </div>

        {sent ? (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center">
            <div className="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
              <Mail className="w-7 h-7 text-green-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">इमेल जाँच गर्नुहोस्</h2>
            <p className="text-gray-600 text-sm mb-6">
              यदि <strong>{email}</strong> मा खाता छ भने, पासवर्ड रिसेट लिंक पठाइएको छ।
              लिंक ३० मिनेटमा म्याद सकिन्छ।
            </p>
            <p className="text-gray-500 text-xs mb-4">
              इमेल आएन? स्प्याम फोल्डर जाँच गर्नुहोस् वा admin लाई सम्पर्क गर्नुहोस्।
            </p>
            <Link
              href="/login"
              className="inline-flex items-center gap-1.5 text-brand-600 hover:text-brand-700 font-medium text-sm"
            >
              <ArrowLeft className="w-4 h-4" />
              लगइनमा फर्कनुहोस्
            </Link>
          </div>
        ) : (
          <form
            onSubmit={handleSubmit}
            className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 space-y-5"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-2.5 rounded-lg border border-gray-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 outline-none transition-all"
                placeholder="you@example.com"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-brand-600 text-white py-2.5 rounded-lg hover:bg-brand-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'पठाउँदै...' : 'रिसेट लिंक पठाउनुहोस्'}
            </button>
          </form>
        )}

        <p className="text-center text-sm text-gray-600 mt-6">
          <Link
            href="/login"
            className="inline-flex items-center gap-1.5 text-brand-600 hover:text-brand-700 font-medium"
          >
            <ArrowLeft className="w-4 h-4" />
            लगइनमा फर्कनुहोस्
          </Link>
        </p>
      </div>
    </div>
  );
}
