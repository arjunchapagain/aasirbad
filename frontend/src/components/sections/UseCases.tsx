'use client';

import { motion } from 'framer-motion';
import { useCasesData } from '@/data/useCases';

interface UseCasesProps {
  language?: 'en' | 'ne';
}

export default function UseCases({ language = 'en' }: UseCasesProps) {
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
          className="font-serif text-5xl md:text-6xl font-bold text-[#2C2C2C] mb-4 text-center"
        >
          {isNepali ? 'वास्तविक कहानीहरु। वास्तविक आवाजहरु। वास्तविक प्रभाव।' : 'Real Stories. Real Voices. Real Impact.'}
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          viewport={{ once: true }}
          className="text-center text-gray-600 mb-16 max-w-2xl mx-auto"
        >
          {isNepali
            ? 'परिवारहरु पहिले नै आफ्नो विरासत संरक्षण गर्दै छन्। यहाँ कसरी छ।'
            : 'Families are already preserving their legacy. Here\'s how.'}
        </motion.p>

        {/* Use Cases Grid */}
        <div className="grid md:grid-cols-2 gap-8">
          {useCasesData.map((useCase, index) => (
            <motion.div
              key={useCase.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="p-8 border-l-4 border-[#C9989A] bg-white hover:shadow-lg transition-shadow rounded"
            >
              {/* Title */}
              <h3 className="font-serif text-2xl font-bold text-[#2C2C2C] mb-4">
                {isNepali ? useCase.titleNe : useCase.title}
              </h3>

              {/* Story */}
              <p className="text-gray-700 leading-relaxed mb-4">
                {isNepali ? useCase.storyNe : useCase.story}
              </p>

              {/* Result */}
              <div className="bg-[#D4A574]/5 p-4 rounded border-l-2 border-[#D4A574]">
                <p className="text-sm font-semibold text-[#8B6F47]">
                  {isNepali ? useCase.resultNe : useCase.result}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
