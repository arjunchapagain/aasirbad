'use client';

import { motion } from 'framer-motion';
import { benefitsData } from '@/data/benefits';

interface WhatIsAasirbadProps {
  language?: 'en' | 'ne';
}

export default function WhatIsAasirbad({ language = 'en' }: WhatIsAasirbadProps) {
  const isNepali = language === 'ne';

  return (
    <section className="py-20 px-6 md:px-12 bg-white">
      <div className="max-w-6xl mx-auto">
        {/* Headline */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="font-serif text-5xl md:text-6xl font-bold text-[#2C2C2C] mb-12 text-center"
        >
          {isNepali ? 'Aasirbad के हो?' : 'What is Aasirbad?'}
        </motion.h2>

        {/* Description */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto mb-16 text-center"
        >
          <p className="text-lg text-gray-700 mb-4 leading-relaxed">
            {isNepali
              ? 'Aasirbad तपाईको परिवारको आवाज भण्डार हो। यो एक सरल, सुरक्षित प्ल्याटफर्म हो जहाँ तपाई आफ्नो प्रियजनहरूलाई रेकर्ड गर्न सक्नुहुन्छ—उनीहरूको कहानी, उनीहरूको बुद्धिमत्ता, उनीहरूको हाँसी—र तीनलाई सदा को लागि सुरक्षित राख्न सक्नुहुन्छ।'
              : 'Aasirbad is your family\'s voice vault. It\'s a simple, secure platform where you can record your loved ones—their stories, their wisdom, their laughter—and preserve them forever.'}
          </p>
          <p className="text-lg text-gray-600 leading-relaxed">
            {isNepali
              ? 'यसलाई आवाजको लागि एक डिजिटल समय क्याप्सुल सोच्नुहोस्। एक ठाउँ जहाँ पुस्ता आफ्नो प्रिय व्यक्तिको शब्द सुन्न सक्छन्, कहिले पनि, कहिँ पनि। क्षणको लामो समय पछि।'
              : 'Think of it as a digital time capsule for voices. A place where generations can listen to the words of those they love, anytime, anywhere. Long after the moment has passed.'}
          </p>
        </motion.div>

        {/* Benefits Cards - 3 Columns */}
        <div className="grid md:grid-cols-3 gap-8">
          {benefitsData.map((benefit, index) => (
            <motion.div
              key={benefit.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="p-8 bg-white border border-gray-100 rounded-lg hover:shadow-lg hover:border-[#D4A574]/30 transition-all"
            >
              {/* Icon */}
              <div className="mb-6 flex justify-start">
                <div className="w-16 h-16 bg-[#D4A574]/10 rounded-lg flex items-center justify-center text-4xl">
                  {benefit.icon}
                </div>
              </div>

              {/* Benefit Title */}
              <h3 className="font-serif text-2xl font-bold text-[#2C2C2C] mb-4">
                {isNepali ? benefit.titleNe : benefit.title}
              </h3>

              {/* Benefit Description */}
              <p className="text-gray-600 leading-relaxed mb-4">
                {isNepali ? benefit.descriptionNe : benefit.description}
              </p>

              {/* Badge */}
              <p className="text-sm text-gray-500 italic">
                {isNepali ? benefit.badgeNe : benefit.badge}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Social Proof Callout */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="mt-16 bg-[#C9989A]/10 border-l-4 border-[#C9989A] p-8 rounded"
        >
          <p className="text-gray-800 italic mb-3">
            💡 {isNepali ? 'वास्तविक परिवारहरु आफ्नो विरासत संरक्षण गर्दै छन्:' : 'Real families are already preserving their legacy:'}
          </p>
          <blockquote className="text-lg font-semibold text-gray-900 mb-2">
            "{isNepali
              ? 'मै हरेक बिहान मेरो बाबाको आवाज सुन्छु। यो जस्तो उनी यहाँ छिन्, मलाई कहानी सुनाइरहेका छन्।'
              : 'I hear my grandfather\'s voice every morning. It\'s like he\'s still here, telling me stories.'}"
          </blockquote>
          <p className="text-sm text-gray-600">
            — {isNepali ? 'प्रिया, मुम्बई' : 'Priya, Mumbai'}
          </p>
        </motion.div>
      </div>
    </section>
  );
}
