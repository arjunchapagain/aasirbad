'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Shield, Users, Heart, Lock } from 'lucide-react';

interface TrustPrivacyProps {
  language?: 'en' | 'ne';
}

const trustPillars = [
  {
    id: 1,
    titleEn: 'Complete Ownership',
    titleNe: 'पूर्ण स्वामित्व',
    icon: '👑',
    descriptionEn: 'Your recordings are 100% yours. Not ours. We never use your voice for AI training, marketing, or any other purpose.',
    descriptionNe: 'तपाईको रेकर्डिङ १००% तपाईको हो। हाम्रो होइन। हामी कहिले पनि तपाईको आवाज AI प्रशिक्षण, विपणन, वा अन्य कुनै प्रयोजनको लागि प्रयोग गर्दैनौँ।',
    pointsEn: [
      'You control who accesses your voice',
      'You can delete everything anytime',
      'Your voice is never sold or shared',
    ],
    pointsNe: [
      'तपाई नियन्त्रण गर्नुहुन्छ कसले तपाईको आवाज पहुँच गर्न सक्छ',
      'तपाई कहिले पनि सबै कुरा मेटाउन सक्नुहुन्छ',
      'तपाईको आवाज कहिले पनि बेचिएको वा साझेदार गरिएको छैन',
    ],
  },
  {
    id: 2,
    titleEn: 'Privacy-First',
    titleNe: 'निजीता-पहिलो',
    icon: '🔐',
    descriptionEn: 'All voice recordings are encrypted both in transit and at rest. We use the same security standards as banks and healthcare providers.',
    descriptionNe: 'सबै आवाज रेकर्डिङ दुबै ट्रान्जिट र आराम समय एनक्रिप्ट गरिन्छ। हामी ब्याङ्क र स्वास्थ्यसेवा प्रदायकहरूको रूपमा समान सुरक्षा मानकहरू प्रयोग गर्छौँ।',
    pointsEn: [
      'End-to-end encryption',
      'Automatic backups',
      'Zero-knowledge architecture',
    ],
    pointsNe: [
      'अन्त-देखि-अन्त एनक्रिप्सन',
      'स्वचालित ब्याकअप',
      'शून्य-ज्ञान आर्किटेक्चर',
    ],
  },
  {
    id: 3,
    titleEn: 'Family Consent',
    titleNe: 'परिवार सहमति',
    icon: '🤝',
    descriptionEn: 'Before sharing any recording, you\'re in control. Who can listen? When? For how long? You decide.',
    descriptionNe: 'कुनै पनि रेकर्डिङ साझेदारी गर्न अघि, तपाई नियन्त्रणमा हुनुहुन्छ। कसले सुन्न सक्छ? कहिले? कति समयको लागि? तपाई निर्णय गर्नुहोस्।',
    pointsEn: [
      'Share with specific family members only',
      'Set time-based access (future generations)',
      'Revoke access anytime',
    ],
    pointsNe: [
      'विशेष परिवार सदस्यहरु जसँग मात्र साझेदारी गर्नुहोस्',
      'समय-आधारित पहुँच सेट गर्नुहोस्',
      'कहिले पनि पहुँच रद्द गर्नुहोस्',
    ],
  },
  {
    id: 4,
    titleEn: 'Legal & Transparent',
    titleNe: 'कानुनी र पारदर्शी',
    icon: '📋',
    descriptionEn: 'Compliant with GDPR, India\'s data protection laws, and privacy standards globally. Our privacy policy is written in plain English.',
    descriptionNe: 'GDPR, भारत को डेटा संरक्षण कानून, र विश्वव्यापी निजीता मानकहरु का साथ अनुपालनशील।',
    pointsEn: [
      'Independent security audits',
      'Transparent data practices',
      'Regular compliance updates',
    ],
    pointsNe: [
      'स्वतन्त्र सुरक्षा अडिट',
      'पारदर्शी डेटा प्रथाहरु',
      'नियमित अनुपालन अपडेट',
    ],
  },
];

export default function TrustPrivacy({ language = 'en' }: TrustPrivacyProps) {
  const isNepali = language === 'ne';

  return (
    <section className="py-20 px-6 md:px-12 bg-[#F8F6F1]">
      <div className="max-w-6xl mx-auto">
        {/* Headline */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="font-serif text-5xl md:text-6xl font-bold text-[#2C2C2C] mb-4 text-center"
        >
          {isNepali ? 'तपाईको आवाज। तपाईको परिवार। तपाईको नियन्त्रण।' : 'Your Voice. Your Family. Your Control.'}
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          viewport={{ once: true }}
          className="text-center text-gray-600 mb-16 max-w-2xl mx-auto"
        >
          {isNepali
            ? 'विश्वास सबै कुरा हो। यहाँ हामी यसलाई कसरी सुरक्षित राख्छौँ।'
            : 'Trust is everything. Here\'s how we protect it.'}
        </motion.p>

        {/* Trust Pillars Grid */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {trustPillars.map((pillar, index) => (
            <motion.div
              key={pillar.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition-shadow"
            >
              {/* Icon + Title */}
              <div className="flex items-center gap-4 mb-4">
                <span className="text-4xl">{pillar.icon}</span>
                <h3 className="font-serif text-2xl font-bold text-[#2C2C2C]">
                  {isNepali ? pillar.titleNe : pillar.titleEn}
                </h3>
              </div>

              {/* Description */}
              <p className="text-gray-700 mb-4">
                {isNepali ? pillar.descriptionNe : pillar.descriptionEn}
              </p>

              {/* Points */}
              <ul className="space-y-2">
                {(isNepali ? pillar.pointsNe : pillar.pointsEn).map((point, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-gray-600">
                    <span className="text-[#D4A574] font-bold mt-1">✓</span>
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Links */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="flex flex-col sm:flex-row justify-center gap-8 text-center"
        >
          <Link href="/privacy" className="text-[#8B6F47] font-semibold hover:underline">
            {isNepali ? 'हाम्रो पूर्ण गोपनीयता नीति पढ्नुहोस् →' : 'Read Our Full Privacy Policy →'}
          </Link>
          <Link href="/data-protection" className="text-[#8B6F47] font-semibold hover:underline">
            {isNepali ? 'डेटा संरक्षण प्रतिश्रुति →' : 'Data Protection Commitments →'}
          </Link>
        </motion.div>
      </div>
    </section>
  );
}
