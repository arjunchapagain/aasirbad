'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { faqData } from '@/data/faq';

interface FAQProps {
  language?: 'en' | 'ne';
}

export default function FAQ({ language = 'en' }: FAQProps) {
  const [openId, setOpenId] = useState<number | null>(null);
  const isNepali = language === 'ne';

  return (
    <section className="py-20 px-6 md:px-12 bg-white">
      <div className="max-w-4xl mx-auto">
        {/* Headline */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="font-serif text-5xl md:text-6xl font-bold text-[#2C2C2C] mb-16 text-center"
        >
          {isNepali ? 'प्रश्नहरु? हामीसँग उत्तर छ।' : 'Questions? We Have Answers.'}
        </motion.h2>

        {/* FAQ Items */}
        <div className="space-y-4">
          {faqData.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: index * 0.05 }}
              viewport={{ once: true }}
              className="border border-gray-200 rounded-lg overflow-hidden"
            >
              {/* Question Header */}
              <button
                onClick={() => setOpenId(openId === item.id ? null : item.id)}
                className="w-full p-6 flex items-center justify-between bg-white hover:bg-[#F8F6F1] transition"
              >
                <h3 className="text-lg font-semibold text-[#2C2C2C] text-left">
                  {isNepali ? item.questionNe : item.question}
                </h3>
                <motion.span
                  animate={{ rotate: openId === item.id ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                  className="text-2xl text-[#D4A574] flex-shrink-0 ml-4"
                >
                  ↓
                </motion.span>
              </button>

              {/* Answer */}
              <AnimatePresence>
                {openId === item.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="p-6 bg-[#F8F6F1] border-t border-gray-200">
                      <p className="text-gray-700 leading-relaxed">
                        {isNepali ? item.answerNe : item.answer}
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
