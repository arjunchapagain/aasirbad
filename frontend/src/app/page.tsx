'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Volume2 } from 'lucide-react';
import HeroSection from '@/components/sections/HeroSection';
import WhatIsAasirbad from '@/components/sections/WhatIsAasirbad';
import HowItWorks from '@/components/sections/HowItWorks';
import UseCases from '@/components/sections/UseCases';
import TrustPrivacy from '@/components/sections/TrustPrivacy';
import FAQ from '@/components/sections/FAQ';
import FinalCTA from '@/components/sections/FinalCTA';

export default function HomePage() {
  const [language, setLanguage] = useState<'en' | 'ne'>('en');
  const isNepali = language === 'ne';

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 flex items-center justify-between px-6 py-4 max-w-7xl mx-auto w-full bg-white/95 backdrop-blur border-b border-gray-100">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#D4A574] to-[#8B6F47] flex items-center justify-center shadow-md">
            <span className="text-white text-lg font-bold">ॐ</span>
          </div>
          <div className="flex flex-col leading-tight">
            <span className="text-xl font-bold text-[#2C2C2C] tracking-tight">Aasirbad</span>
            <span className="text-[10px] text-[#8B6F47] font-medium -mt-0.5">आसिर्बाद</span>
          </div>
        </Link>
        <div className="flex items-center gap-4">
          {/* Language Toggle */}
          <div className="flex items-center gap-2 border border-gray-200 rounded-lg p-1">
            <button
              onClick={() => setLanguage('en')}
              className={`px-3 py-1 rounded transition-colors ${
                language === 'en'
                  ? 'bg-[#8B6F47] text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              EN
            </button>
            <button
              onClick={() => setLanguage('ne')}
              className={`px-3 py-1 rounded transition-colors ${
                language === 'ne'
                  ? 'bg-[#8B6F47] text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              नेपाली
            </button>
          </div>
          <Link
            href="/login"
            className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
          >
            {isNepali ? 'साइन इन' : 'Sign In'}
          </Link>
          <Link
            href="/register"
            className="text-sm font-medium bg-[#8B6F47] text-white px-5 py-2 rounded-lg hover:bg-[#6F5A37] transition-all shadow-md"
          >
            {isNepali ? 'सुरु गर्नुहोस्' : 'Get Started'}
          </Link>
        </div>
      </nav>

      {/* All Sections */}
      <HeroSection language={language} />
      <WhatIsAasirbad language={language} />
      <HowItWorks language={language} />
      <UseCases language={language} />
      <TrustPrivacy language={language} />
      <FAQ language={language} />
      <FinalCTA language={language} />

      {/* Footer */}
      <footer className="border-t border-gray-200 py-8 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-[#8B6F47] font-bold">ॐ</span>
            <span className="text-sm text-gray-600">
              &copy; 2026 Aasirbad. {isNepali ? 'सबै अधिकार सुरक्षित।' : 'All rights reserved.'}
            </span>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-600">
            <Link href="/privacy" className="hover:text-[#8B6F47] transition">
              {isNepali ? 'गोपनीयता' : 'Privacy'}
            </Link>
            <Link href="/terms" className="hover:text-[#8B6F47] transition">
              {isNepali ? 'सर्तहरू' : 'Terms'}
            </Link>
            <Link href="/contact" className="hover:text-[#8B6F47] transition">
              {isNepali ? 'सम्पर्क' : 'Contact'}
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
