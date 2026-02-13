'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Mic, Wand2, PlayCircle, ArrowRight } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
            <Mic className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-gray-900">VoiceForge</span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/login"
            className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="text-sm font-medium bg-brand-600 text-white px-4 py-2 rounded-lg hover:bg-brand-700 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 pt-20 pb-32">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-4xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 bg-brand-50 border border-brand-200 rounded-full px-4 py-1.5 mb-8">
            <span className="w-2 h-2 rounded-full bg-brand-500 animate-pulse" />
            <span className="text-sm font-medium text-brand-700">
              Powered by Tortoise TTS
            </span>
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 leading-tight tracking-tight">
            Clone Any Voice
            <br />
            <span className="text-brand-600">With Precision</span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Record voice samples, train a custom AI model, and generate
            natural-sounding speech that captures every nuance of the original
            voice.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/register"
              className="flex items-center gap-2 bg-brand-600 text-white px-8 py-3.5 rounded-xl hover:bg-brand-700 transition-all text-lg font-medium shadow-lg shadow-brand-600/25 hover:shadow-xl hover:shadow-brand-600/30"
            >
              Start Cloning
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/demo"
              className="flex items-center gap-2 text-gray-700 px-8 py-3.5 rounded-xl border border-gray-200 hover:border-gray-300 hover:bg-white transition-all text-lg font-medium"
            >
              <PlayCircle className="w-5 h-5" />
              Listen to Demo
            </Link>
          </div>
        </motion.div>

        {/* How It Works */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-32"
        >
          <h2 className="text-center text-3xl font-bold text-gray-900 mb-16">
            How It Works
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Mic,
                step: '01',
                title: 'Record Voice Samples',
                description:
                  'Share a recording link with your speaker. They read 20 diverse prompts covering different phonemes, emotions, and speech patterns.',
              },
              {
                icon: Wand2,
                step: '02',
                title: 'AI Training',
                description:
                  'Our engine preprocesses audio (noise reduction, normalization) and extracts voice conditioning latents that capture the unique vocal identity.',
              },
              {
                icon: PlayCircle,
                step: '03',
                title: 'Generate Speech',
                description:
                  'Type any text and hear it spoken in the cloned voice. Choose from multiple quality presets for speed vs. fidelity tradeoff.',
              },
            ].map((item) => (
              <div
                key={item.step}
                className="relative bg-white rounded-2xl p-8 border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
              >
                <span className="text-6xl font-bold text-gray-100 absolute top-4 right-6">
                  {item.step}
                </span>
                <div className="w-12 h-12 rounded-xl bg-brand-50 flex items-center justify-center mb-4">
                  <item.icon className="w-6 h-6 text-brand-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {item.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mt-32"
        >
          <h2 className="text-center text-3xl font-bold text-gray-900 mb-4">
            Professional Grade Features
          </h2>
          <p className="text-center text-gray-600 mb-16 max-w-2xl mx-auto">
            Built with industry best practices for production voice cloning
          </p>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { title: 'Noise Reduction', desc: 'Spectral gating removes background noise while preserving voice clarity' },
              { title: 'Quality Validation', desc: 'Automatic SNR, clipping, and silence detection ensures clean training data' },
              { title: 'Real-time Progress', desc: 'WebSocket-powered live training status updates with progress tracking' },
              { title: 'Multiple Presets', desc: 'Ultra-fast to high-quality synthesis presets for any use case' },
              { title: 'Secure by Design', desc: 'JWT authentication, presigned URLs, and encrypted storage' },
              { title: 'Cloud Native', desc: 'Horizontal scaling with GPU workers, S3 storage, and Redis queues' },
            ].map((feature) => (
              <div
                key={feature.title}
                className="bg-white/60 backdrop-blur rounded-xl p-6 border border-gray-100"
              >
                <h4 className="font-semibold text-gray-900 mb-1">
                  {feature.title}
                </h4>
                <p className="text-sm text-gray-600">{feature.desc}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-8">
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
          <span className="text-sm text-gray-500">
            &copy; 2026 VoiceForge. All rights reserved.
          </span>
          <div className="flex items-center gap-6 text-sm text-gray-500">
            <a href="#" className="hover:text-gray-700">Privacy</a>
            <a href="#" className="hover:text-gray-700">Terms</a>
            <a href="#" className="hover:text-gray-700">Docs</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
