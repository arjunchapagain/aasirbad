'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

interface HowItWorksProps {
  language?: 'en' | 'ne';
}

const steps = [
  {
    id: 1,
    titleEn: 'Record Their Voice',
    titleNe: 'उनीहरूको आवाज रेकर्ड गर्नुहोस्',
    descriptionEn: 'Record your loved one\'s story, blessing, lullaby, or memory. Keep it natural. We handle the rest. Your recordings are automatically enhanced and preserved.',
    descriptionNe: 'तपाईको प्रियजनको कहानी, आशीर्वाद, लोरी, वा स्मृति रेकर्ड गर्नुहोस्। यसलाई स्वाभाविक राख्नुहोस्। बाँकी काम हामीले गर्छौँ।',
    detailsEn: 'Time: 2-30 minutes (you decide)',
    detailsNe: 'समय: २-३० मिनेट (तपाई निर्णय गर्नुहोस्)',
    icon: '🎤',
  },
  {
    id: 2,
    titleEn: 'Safe & Secure Storage',
    titleNe: 'सुरक्षित भण्डारण',
    descriptionEn: 'Your voice is encrypted and stored safely. Only you control who can access it. Your voice, your family, your rules.',
    descriptionNe: 'तपाईको आवाज एनक्रिप्ट गरिएको र सुरक्षित भण्डारण गरिन्छ। केवल तपाई नियन्त्रण गर्नुहुन्छ कसले पहुँच गर्न सक्छ।',
    detailsEn: 'Tech: Military-grade encryption, automatic backups',
    detailsNe: 'प्रविधि: सैन्य-ग्रेड एनक्रिप्सन, स्वचालित ब्याकअप',
    icon: '🔒',
  },
  {
    id: 3,
    titleEn: 'Share Across Generations',
    titleNe: 'पुस्ताहरू जुरिपिक साझेदारी गर्नुहोस्',
    descriptionEn: 'Create a private link to share with family. Or keep it just for yourself. You decide. Your loved ones can listen anytime.',
    descriptionNe: 'परिवारको साथ साझेदारी गर्न निजी लिङ्क सिर्जना गर्नुहोस्। वा यसलाई केवल आफ्नो लागि राख्नुहोस्। तपाई निर्णय गर्नुहोस्।',
    detailsEn: 'Access: Mobile, web, or download for offline listening',
    detailsNe: 'पहुँच: मोबाइल, वेब, वा अफलाइन सुनाइको लागि डाउनलोड',
    icon: '❤️',
  },
];

export default function HowItWorks({ language = 'en' }: HowItWorksProps) {
  const isNepali = language === 'ne';

  return (
    <section id="how-it-works" className="py-20 px-6 md:px-12 bg-[#F8F6F1]">
      <div className="max-w-6xl mx-auto">
        {/* Headline */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="font-serif text-5xl md:text-6xl font-bold text-[#2C2C2C] mb-16 text-center"
        >
          {isNepali ? 'कसरी काम गर्छ: ३ सरल चरण' : 'How It Works: 3 Simple Steps'}
        </motion.h2>

        {/* Steps Container */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {steps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="relative"
            >
              {/* Step Number Circle */}
              <div className="absolute -top-6 -left-3 w-12 h-12 bg-[#D4A574] text-white rounded-full flex items-center justify-center font-bold text-lg shadow-md">
                {step.id}
              </div>

              {/* Card */}
              <div className="bg-white p-8 rounded-lg shadow-md h-full pt-12 hover:shadow-lg transition-shadow">
                {/* Icon */}
                <div className="text-5xl mb-4">{step.icon}</div>

                {/* Title */}
                <h3 className="font-serif text-2xl font-bold text-[#2C2C2C] mb-4">
                  {isNepali ? step.titleNe : step.titleEn}
                </h3>

                {/* Description */}
                <p className="text-gray-700 mb-6 leading-relaxed">
                  {isNepali ? step.descriptionNe : step.descriptionEn}
                </p>

                {/* Details */}
                <p className="text-sm text-gray-500 italic">
                  {isNepali ? step.detailsNe : step.detailsEn}
                </p>
              </div>

              {/* Arrow (hidden on last item) */}
              {index < steps.length - 1 && (
                <div className="hidden md:flex absolute top-1/2 -right-4 translate-y-1/2 text-2xl text-[#D4A574]">
                  →
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <p className="text-gray-700 mb-4 font-semibold">
            {isNepali ? 'सुरु गर्न तयार हुनुहुन्छ?' : 'Ready to start recording?'}
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link href="/register">
              <button className="px-6 py-3 bg-[#8B6F47] text-white rounded-lg font-semibold hover:bg-[#6F5A37] transition">
                {isNepali ? 'निःशुल्क शुरु गर्नुहोस्' : 'Start Free'}
              </button>
            </Link>
            <button className="px-6 py-3 bg-white text-[#8B6F47] border-2 border-[#8B6F47] rounded-lg font-semibold hover:bg-gray-50 transition">
              {isNepali ? 'डेमो हेर्नुहोस्' : 'Schedule Demo'}
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
