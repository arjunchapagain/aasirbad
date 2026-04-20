'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

interface FinalCTAProps {
  language?: 'en' | 'ne';
}

export default function FinalCTA({ language = 'en' }: FinalCTAProps) {
  const isNepali = language === 'ne';

  return (
    <section className="py-20 px-6 md:px-12 bg-gradient-to-r from-[#8B6F47] to-[#A0865A] text-white">
      <div className="max-w-4xl mx-auto text-center">
        {/* Headline */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="font-serif text-5xl md:text-6xl font-bold mb-6"
        >
          {isNepali
            ? 'तपाईको परिवारको आवाज सदा को लागि रहनु चाहिन्छ'
            : 'Your Family\'s Voice Deserves to Last Forever'}
        </motion.h2>

        {/* Subheading */}
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          viewport={{ once: true }}
          className="text-xl mb-12 opacity-95"
        >
          {isNepali
            ? 'हजारौँ परिवारहरु आफ्नो विरासत संरक्षण गर्दै छन्।\nमात्र ३ मिनेटमा शुरु गर्नुहोस्। नि: शुल्क।'
            : 'Join thousands of families preserving their legacy.\nStart recording in 3 minutes. Free.'}
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
          className="flex flex-col sm:flex-row justify-center gap-4 mb-12"
        >
          <Link href="/register">
            <button className="px-8 py-4 bg-white text-[#8B6F47] rounded-lg font-semibold hover:bg-gray-100 transition shadow-lg">
              {isNepali ? 'आफ्नो पहिलो कहानी रेकर्ड गर्नुहोस् नि: शुल्क' : 'Record Your First Story Free'}
            </button>
          </Link>
          <button className="px-8 py-4 border-2 border-white text-white rounded-lg font-semibold hover:bg-white/10 transition">
            {isNepali ? '२ मिनेटको डेमो हेर्नुहोस्' : 'Watch a 2-min Demo'}
          </button>
        </motion.div>

        {/* Social Proof */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="flex flex-col sm:flex-row justify-center gap-8 text-sm mb-12"
        >
          <span>⭐ 4.8/5 {isNepali ? 'तारा' : 'stars'} {isNepali ? 'सबै परिवारबाट' : 'from'} 2,400+ {isNepali ? 'परिवार' : 'families'}</span>
          <span>✓ {isNepali ? 'प्रयोग हुन्छ' : 'Used in'} 15 {isNepali ? 'देशहरुमा' : 'countries'}</span>
          <span>✓ {isNepali ? 'सुरक्षित गरिएको' : 'Over'} 50,000 {isNepali ? 'रेकर्डिङ संरक्षित' : 'recordings preserved'}</span>
        </motion.div>

        {/* Final Message */}
        <motion.blockquote
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="border-l-4 border-white pl-6 py-6 text-lg italic max-w-2xl mx-auto"
        >
          "{isNepali
            ? 'सर्वोत्तम समय कल रेकर्ड गर्न कल था। दोस्रो सर्वोत्तम समय आज हो।'
            : 'The best time to record was yesterday. The second best time is today.'}"
          <br />
          <span className="text-sm font-semibold mt-3 block text-right not-italic">
            {isNepali ? 'सही पल प्रतीक्षा गर्नुहोस् नगर्नुहोस्। यसलाई सिर्जना गर्नुहोस्।' : 'Don\'t wait for the right moment. Create it.'}
          </span>
        </motion.blockquote>
      </div>
    </section>
  );
}
