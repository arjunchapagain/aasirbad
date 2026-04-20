'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Volume2 } from 'lucide-react';

interface HeroSectionProps {
  language?: 'en' | 'ne';
}

export default function HeroSection({ language = 'en' }: HeroSectionProps) {
  const isNepali = language === 'ne';

  return (
    <section className="relative w-full min-h-screen bg-gradient-to-br from-[#F8F6F1] to-[#EBE3D7] flex items-center">
      {/* Background overlay */}
      <div className="absolute inset-0 opacity-10 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0dCBlcm4zZD0iTTMwIDAgQzMwIDAgMzAgMjAgMzAgMzAgQzMwIDMwIDAgMzAgMzAgMzAgQzMwIDMwIDMwIDMwIDAgMzAgQzAgMzAgMzAgMCAwIDAgQzMwIDAgMzAgMzAgMzAgMzAiIHN0cm9rZT0iIzhCNkY0NyIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz48L3N2Zz4=')] opacity-5" />

      <div className="max-w-7xl mx-auto px-6 py-20 w-full relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl"
        >
          {/* Headline */}
          <h1 className="font-serif text-6xl md:text-7xl font-bold text-[#2C2C2C] mb-6 leading-tight">
            {isNepali ? (
              <>
                हामीले प्रेम गरेको<br />
                <span className="text-[#D4A574]">आवाज, सदा को लागि</span>
              </>
            ) : (
              <>
                The Voices We Love,<br />
                <span className="text-[#D4A574]">Forever</span>
              </>
            )}
          </h1>

          {/* Subheading */}
          <p className="text-xl md:text-2xl text-gray-700 mb-8 max-w-3xl leading-relaxed font-light">
            {isNepali
              ? 'आफ्नो आमा-बाबु को आशीर्वाद, दिदी-भाइ को कहानी, र पारिवारिक बुद्धिमत्ता आफ्नो आवाजमा सुरक्षित राख्नुहोस्। त्यो बहुमूल्य आवाज कहिले पनि हराउनुहुन्न।'
              : 'Preserve your parents\' blessings, grandparents\' stories, and family wisdom in their own voice. Never lose that precious sound again.'}
          </p>

          {/* Trust Badges */}
          <div className="flex flex-wrap gap-6 mb-12 text-sm text-gray-600">
            <span className="flex items-center gap-2">
              <span className="text-[#D4A574]">✓</span> {isNepali ? 'निःशुल्क शुरु गर्नुहोस्' : 'Free to start'}
            </span>
            <span className="flex items-center gap-2">
              <span className="text-[#D4A574]">✓</span> {isNepali ? 'तपाईको आवाज, तपाईको डेटा' : 'Your voice, your data'}
            </span>
            <span className="flex items-center gap-2">
              <span className="text-[#D4A574]">✓</span> {isNepali ? 'निजी र सुरक्षित' : 'Private & secure'}
            </span>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Link href="/register">
              <button className="px-8 py-4 bg-[#8B6F47] text-white rounded-lg font-semibold hover:bg-[#6F5A37] transition-all shadow-lg hover:shadow-xl">
                {isNepali ? 'आवाज सुरक्षित गर्नुहोस्' : 'Start Recording Free'}
              </button>
            </Link>
            <button
              onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
              className="px-8 py-4 bg-white text-[#8B6F47] border-2 border-[#8B6F47] rounded-lg font-semibold hover:bg-gray-50 transition-all flex items-center justify-center gap-2"
            >
              <Volume2 className="w-5 h-5" />
              {isNepali ? 'कसरी काम गर्छ?' : 'See How It Works'}
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
