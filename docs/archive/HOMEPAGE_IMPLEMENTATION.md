# Aasirbad Homepage - Implementation Guide
## React/Next.js Component Structure & Code Recommendations

---

## 📁 FILE STRUCTURE

```
frontend/src/
├── app/
│   ├── layout.tsx (main layout with nav, footer)
│   ├── page.tsx (HOMEPAGE - entry point)
│   └── globals.css
├── components/
│   ├── sections/
│   │   ├── HeroSection.tsx
│   │   ├── WhatIsAasirbad.tsx
│   │   ├── HowItWorks.tsx
│   │   ├── UseCases.tsx
│   │   ├── TrustPrivacy.tsx
│   │   ├── FAQ.tsx
│   │   └── FinalCTA.tsx
│   ├── shared/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Section.tsx
│   │   └── Badge.tsx
│   └── Navigation.tsx
├── data/
│   ├── useCases.ts
│   ├── faq.ts
│   ├── benefits.ts
│   └── seo.ts
├── hooks/
│   └── useLanguage.ts (i18n support)
└── styles/
    ├── colors.ts
    ├── spacing.ts
    └── typography.ts
```

---

## 🎯 HERO SECTION COMPONENT

```tsx
// components/sections/HeroSection.tsx
'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';

export default function HeroSection() {
  return (
    <section className="relative w-full h-screen bg-gradient-to-br from-[#F8F6F1] to-[#EBE3D7]">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0 overflow-hidden">
        <Image
          src="/images/hero-family-multigenerational.jpg"
          alt="Multigenerational family moment"
          fill
          className="object-cover opacity-40"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-r from-black/30 to-transparent"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 flex items-center justify-center h-full">
        <div className="max-w-4xl px-6 md:px-12 text-center">
          {/* Main Headline */}
          <h1 className="font-serif text-5xl md:text-7xl font-bold text-[#2C2C2C] mb-6 leading-tight">
            The Voices We Love,<br />
            Forever
          </h1>

          {/* Subheading */}
          <p className="text-lg md:text-2xl text-gray-700 mb-8 max-w-2xl mx-auto leading-relaxed font-light">
            Preserve your parents' blessings, grandparents' stories, and family 
            wisdom in their own voice. Never lose that precious sound again.
          </p>

          {/* Trust Badges */}
          <div className="flex flex-wrap justify-center gap-6 mb-12 text-sm text-gray-600">
            <span className="flex items-center gap-2">
              <span className="text-[#D4A574]">✓</span> Free to start
            </span>
            <span className="flex items-center gap-2">
              <span className="text-[#D4A574]">✓</span> Your voice, your data
            </span>
            <span className="flex items-center gap-2">
              <span className="text-[#D4A574]">✓</span> Private & secure
            </span>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row justify-center gap-4 mb-8">
            <Link href="/record">
              <button className="px-8 py-4 bg-[#8B6F47] text-white rounded-lg font-semibold hover:bg-[#6F5A37] transition-colors shadow-lg">
                Start Recording Free
              </button>
            </Link>
            <button 
              onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
              className="px-8 py-4 bg-white text-[#8B6F47] border-2 border-[#8B6F47] rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              See How It Works →
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
```

---

## 📖 WHAT IS AASIRBAD SECTION

```tsx
// components/sections/WhatIsAasirbad.tsx
'use client';

import React from 'react';
import { benefitsData } from '@/data/benefits';
import Card from '@/components/shared/Card';

export default function WhatIsAasirbad() {
  return (
    <section className="py-20 px-6 md:px-12 bg-white">
      <div className="max-w-6xl mx-auto">
        {/* Headline */}
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-[#2C2C2C] mb-12 text-center">
          What is Aasirbad?
        </h2>

        {/* Description */}
        <div className="max-w-3xl mx-auto mb-16 text-center">
          <p className="text-lg text-gray-700 mb-4 leading-relaxed">
            Aasirbad is your family's voice vault. It's a simple, secure platform 
            where you can record your loved ones—their stories, their wisdom, their 
            laughter—and preserve them forever.
          </p>
          <p className="text-lg text-gray-600 leading-relaxed">
            Think of it as a digital time capsule for voices. A place where generations 
            can listen to the words of those they love, anytime, anywhere. Long after 
            the moment has passed.
          </p>
        </div>

        {/* Benefits Cards - 3 Columns */}
        <div className="grid md:grid-cols-3 gap-8">
          {benefitsData.map((benefit) => (
            <Card key={benefit.id} className="p-8 text-center hover:shadow-lg transition">
              {/* Icon */}
              <div className="mb-6 flex justify-center">
                <div className="w-16 h-16 bg-[#D4A574]/10 rounded-full flex items-center justify-center text-3xl">
                  {benefit.icon}
                </div>
              </div>

              {/* Benefit Title */}
              <h3 className="font-serif text-2xl font-bold text-[#2C2C2C] mb-4">
                {benefit.title}
              </h3>

              {/* Benefit Description */}
              <p className="text-gray-600 leading-relaxed mb-4">
                {benefit.description}
              </p>

              {/* Badge */}
              {benefit.badge && (
                <p className="text-sm text-gray-500 italic">
                  {benefit.badge}
                </p>
              )}
            </Card>
          ))}
        </div>

        {/* Social Proof Callout */}
        <div className="mt-16 bg-[#C9989A]/10 border-l-4 border-[#C9989A] p-8 rounded">
          <p className="text-gray-800 italic mb-3">
            💡 Real families are already preserving their legacy:
          </p>
          <blockquote className="text-lg font-semibold text-gray-900 mb-2">
            "I hear my grandfather's voice every morning. It's like he's still here, 
            telling me stories."
          </blockquote>
          <p className="text-sm text-gray-600">— Priya, Mumbai</p>
        </div>
      </div>
    </section>
  );
}
```

---

## 🚀 HOW IT WORKS SECTION

```tsx
// components/sections/HowItWorks.tsx
'use client';

import React from 'react';

const steps = [
  {
    id: 1,
    title: 'Record Their Voice',
    description: 'Record your loved one\'s story, blessing, lullaby, or memory. Keep it natural. We handle the rest. Your recordings are automatically enhanced and preserved.',
    details: 'Time: 2-30 minutes (you decide)',
    icon: '🎤',
  },
  {
    id: 2,
    title: 'Safe & Secure Storage',
    description: 'Your voice is encrypted and stored safely. Only you control who can access it. Your voice, your family, your rules.',
    details: 'Tech: Military-grade encryption, automatic backups',
    icon: '🔒',
  },
  {
    id: 3,
    title: 'Share Across Generations',
    description: 'Create a private link to share with family. Or keep it just for yourself. You decide. Your loved ones can listen anytime.',
    details: 'Access: Mobile, web, or download for offline listening',
    icon: '❤️',
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20 px-6 md:px-12 bg-[#F8F6F1]">
      <div className="max-w-6xl mx-auto">
        {/* Headline */}
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-[#2C2C2C] mb-16 text-center">
          How It Works:<br className="hidden sm:block" /> 3 Simple Steps
        </h2>

        {/* Steps Container */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {steps.map((step, index) => (
            <div key={step.id} className="relative">
              {/* Step Number Circle */}
              <div className="absolute -top-6 -left-3 w-12 h-12 bg-[#D4A574] text-white rounded-full flex items-center justify-center font-bold text-lg">
                {step.id}
              </div>

              {/* Card */}
              <div className="bg-white p-8 rounded-lg shadow-md h-full pt-12">
                {/* Icon */}
                <div className="text-5xl mb-4">{step.icon}</div>

                {/* Title */}
                <h3 className="font-serif text-2xl font-bold text-[#2C2C2C] mb-4">
                  {step.title}
                </h3>

                {/* Description */}
                <p className="text-gray-700 mb-6 leading-relaxed">
                  {step.description}
                </p>

                {/* Details */}
                <p className="text-sm text-gray-500 italic">
                  {step.details}
                </p>
              </div>

              {/* Arrow (hidden on last item) */}
              {index < steps.length - 1 && (
                <div className="hidden md:flex absolute top-1/2 -right-4 translate-y-1/2 text-2xl text-[#D4A574]">
                  →
                </div>
              )}
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="text-center">
          <p className="text-gray-700 mb-4 font-semibold">Ready to start recording?</p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <button className="px-6 py-3 bg-[#8B6F47] text-white rounded-lg font-semibold hover:bg-[#6F5A37] transition">
              Start Free
            </button>
            <button className="px-6 py-3 bg-white text-[#8B6F47] border-2 border-[#8B6F47] rounded-lg font-semibold hover:bg-gray-50 transition">
              Schedule Demo
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
```

---

## 💝 USE CASES SECTION

```tsx
// components/sections/UseCases.tsx
'use client';

import React from 'react';
import { useCasesData } from '@/data/useCases';
import Card from '@/components/shared/Card';

export default function UseCases() {
  return (
    <section className="py-20 px-6 md:px-12 bg-white">
      <div className="max-w-6xl mx-auto">
        {/* Headline */}
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-[#2C2C2C] mb-4 text-center">
          Real Stories. Real Voices. Real Impact.
        </h2>
        <p className="text-center text-gray-600 mb-16 max-w-2xl mx-auto">
          Families are already preserving their legacy. Here's how.
        </p>

        {/* Use Cases Grid */}
        <div className="grid md:grid-cols-2 gap-8">
          {useCasesData.map((useCase) => (
            <Card key={useCase.id} className="p-8 border-l-4 border-[#C9989A] hover:shadow-lg transition">
              {/* Title */}
              <h3 className="font-serif text-2xl font-bold text-[#2C2C2C] mb-4">
                {useCase.title}
              </h3>

              {/* Story */}
              <p className="text-gray-700 leading-relaxed mb-4">
                {useCase.story}
              </p>

              {/* Result */}
              <div className="bg-[#D4A574]/5 p-4 rounded border-l-2 border-[#D4A574]">
                <p className="text-sm font-semibold text-[#8B6F47]">
                  {useCase.result}
                </p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
```

---

## 🛡️ TRUST & PRIVACY SECTION

```tsx
// components/sections/TrustPrivacy.tsx
'use client';

import React from 'react';

const trustPillars = [
  {
    id: 1,
    title: 'Complete Ownership',
    icon: '👑',
    points: [
      'You control who accesses your voice',
      'You can delete everything anytime',
      'Your voice is never sold or shared',
    ],
    description: 'Your recordings are 100% yours. Not ours. We never use your voice for AI training, marketing, or any other purpose.',
  },
  {
    id: 2,
    title: 'Privacy-First',
    icon: '🔐',
    points: [
      'End-to-end encryption',
      'Automatic backups',
      'Zero-knowledge architecture',
    ],
    description: 'All voice recordings are encrypted both in transit and at rest. We use the same security standards as banks and healthcare providers.',
  },
  {
    id: 3,
    title: 'Family Consent',
    icon: '🤝',
    points: [
      'Share with specific family members only',
      'Set time-based access (future generations)',
      'Revoke access anytime',
    ],
    description: 'Before sharing any recording, you\'re in control. Who can listen? When? For how long? You decide.',
  },
  {
    id: 4,
    title: 'Legal & Transparent',
    icon: '📋',
    points: [
      'Independent security audits',
      'Transparent data practices',
      'Regular compliance updates',
    ],
    description: 'Compliant with GDPR, India\'s data protection laws, and privacy standards globally. Our privacy policy is written in plain English.',
  },
];

export default function TrustPrivacy() {
  return (
    <section className="py-20 px-6 md:px-12 bg-[#F8F6F1]">
      <div className="max-w-6xl mx-auto">
        {/* Headline */}
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-[#2C2C2C] mb-4 text-center">
          Your Voice. Your Family. Your Control.
        </h2>
        <p className="text-center text-gray-600 mb-16 max-w-2xl mx-auto">
          Trust is everything. Here's how we protect it.
        </p>

        {/* Trust Pillars Grid */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {trustPillars.map((pillar) => (
            <div key={pillar.id} className="bg-white p-8 rounded-lg shadow-md">
              {/* Icon + Title */}
              <div className="flex items-center gap-4 mb-4">
                <span className="text-4xl">{pillar.icon}</span>
                <h3 className="font-serif text-2xl font-bold text-[#2C2C2C]">
                  {pillar.title}
                </h3>
              </div>

              {/* Description */}
              <p className="text-gray-700 mb-4">
                {pillar.description}
              </p>

              {/* Points */}
              <ul className="space-y-2">
                {pillar.points.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-gray-600">
                    <span className="text-[#D4A574] font-bold mt-1">✓</span>
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Links */}
        <div className="flex flex-col sm:flex-row justify-center gap-8 text-center">
          <a href="/privacy" className="text-[#8B6F47] font-semibold hover:underline">
            Read Our Full Privacy Policy →
          </a>
          <a href="/data-protection" className="text-[#8B6F47] font-semibold hover:underline">
            Data Protection Commitments →
          </a>
        </div>
      </div>
    </section>
  );
}
```

---

## ❓ FAQ SECTION

```tsx
// components/sections/FAQ.tsx
'use client';

import React, { useState } from 'react';
import { faqData } from '@/data/faq';

export default function FAQ() {
  const [openId, setOpenId] = useState<number | null>(null);

  return (
    <section className="py-20 px-6 md:px-12 bg-white">
      <div className="max-w-4xl mx-auto">
        {/* Headline */}
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-[#2C2C2C] mb-16 text-center">
          Questions? We Have Answers.
        </h2>

        {/* FAQ Items */}
        <div className="space-y-4">
          {faqData.map((item) => (
            <div key={item.id} className="border border-gray-200 rounded-lg overflow-hidden">
              {/* Question Header */}
              <button
                onClick={() => setOpenId(openId === item.id ? null : item.id)}
                className="w-full p-6 flex items-center justify-between bg-white hover:bg-[#F8F6F1] transition"
              >
                <h3 className="text-lg font-semibold text-[#2C2C2C] text-left">
                  {item.question}
                </h3>
                <span className={`text-2xl text-[#D4A574] transition-transform ${
                  openId === item.id ? 'rotate-180' : ''
                }`}>
                  ↓
                </span>
              </button>

              {/* Answer */}
              {openId === item.id && (
                <div className="p-6 bg-[#F8F6F1] border-t border-gray-200">
                  <p className="text-gray-700 leading-relaxed">
                    {item.answer}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

---

## 🎬 FINAL CTA SECTION

```tsx
// components/sections/FinalCTA.tsx
'use client';

import React from 'react';
import Link from 'next/link';

export default function FinalCTA() {
  return (
    <section className="py-20 px-6 md:px-12 bg-gradient-to-r from-[#8B6F47] to-[#A0865A] text-white">
      <div className="max-w-4xl mx-auto text-center">
        {/* Headline */}
        <h2 className="font-serif text-4xl md:text-5xl font-bold mb-6">
          Your Family's Voice Deserves to Last Forever
        </h2>

        {/* Subheading */}
        <p className="text-xl mb-12 opacity-95">
          Join thousands of families preserving their legacy.<br />
          Start recording in 3 minutes. Free.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-12">
          <Link href="/record">
            <button className="px-8 py-4 bg-white text-[#8B6F47] rounded-lg font-semibold hover:bg-gray-100 transition shadow-lg">
              Record Your First Story Free
            </button>
          </Link>
          <button className="px-8 py-4 border-2 border-white text-white rounded-lg font-semibold hover:bg-white/10 transition">
            Watch a 2-min Demo
          </button>
        </div>

        {/* Social Proof */}
        <div className="flex flex-col sm:flex-row justify-center gap-8 text-sm mb-12">
          <span>⭐ 4.8/5 stars from 2,400+ families</span>
          <span>✓ Used in 15 countries</span>
          <span>✓ Over 50,000 recordings preserved</span>
        </div>

        {/* Final Message */}
        <blockquote className="border-l-4 border-white pl-6 py-6 text-lg italic max-w-2xl mx-auto">
          "The best time to record was yesterday. The second best time is today."
          <br />
          <span className="text-sm font-semibold mt-3 block text-right not-italic">
            Don't wait for the right moment. Create it.
          </span>
        </blockquote>
      </div>
    </section>
  );
}
```

---

## 📊 DATA FILES

```typescript
// data/benefits.ts
export const benefitsData = [
  {
    id: 1,
    icon: '🎤',
    title: 'Simple Recording',
    description: 'No technical skills needed. Record on any device—phone, tablet, or computer. One click. That\'s it.',
    badge: 'Designed for everyone'
  },
  {
    id: 2,
    icon: '🛡️',
    title: 'Forever Preserved',
    description: 'Your recordings are secure, backed up, and accessible to your family whenever they need to hear that voice.',
    badge: 'Automatic backup'
  },
  {
    id: 3,
    icon: '❤️',
    title: 'Shared Legacy',
    description: 'Let your children, grandchildren, and generations to come experience the real voice of their ancestors.',
    badge: 'Generational access'
  },
];
```

```typescript
// data/useCases.ts
export const useCasesData = [
  {
    id: 1,
    title: 'A Grandmother\'s Blessings for Life',
    story: 'Meena\'s grandmother has been telling family blessings for 50 years. "I was afraid when she\'d be gone, we\'d lose those words forever," Meena says. "Now my children hear them in her voice. They listen before exams, before big days. It\'s like she\'s still here, protecting them." Meena recorded her grandmother\'s morning blessings, prayers, and wisdom in just one afternoon. Her 3 kids, 2 cousins, and growing family all have access.',
    result: 'A family tradition preserved. A voice that lasts forever.',
  },
  // Add remaining use cases...
];
```

```typescript
// data/faq.ts
export const faqData = [
  {
    id: 1,
    question: 'Who can use Aasirbad?',
    answer: 'Anyone who wants to preserve a loved one\'s voice. Whether you\'re a child recording a parent\'s blessing, a parent preserving a grandparent\'s stories, or a grandchild wanting to hear their grandfather\'s voice—Aasirbad is for you. You need just a smartphone, tablet, or computer and an internet connection to start.',
  },
  // Add remaining FAQs...
];
```

```typescript
// data/seo.ts
export const seoConfig = {
  title: 'Aasirbad | Preserve Your Loved One\'s Voice Forever',
  description: 'Record, preserve, and share the voices of parents, grandparents, and loved ones. An AI-powered platform for capturing family stories, blessings, and memories.',
  keywords: [
    'voice preservation',
    'family memories',
    'AI voice recording',
    'grandparent stories',
  ],
};
```

---

## 🎨 TAILWIND CONFIG ADDITIONS

```typescript
// tailwind.config.ts - Add these custom colors
export default {
  theme: {
    extend: {
      colors: {
        'warm-gold': '#D4A574',
        'warm-brown': '#8B6F47',
        'warm-white': '#F8F6F1',
        'warm-beige': '#EBE3D7',
        'deep-charcoal': '#2C2C2C',
        'soft-rose': '#C9989A',
      },
      fontFamily: {
        'serif': ['Georgia', 'Crimson Text', 'serif'],
      },
    },
  },
};
```

---

## 📱 RESPONSIVE DESIGN NOTES

- **Mobile-first approach**: Design for mobile, then scale up
- **Hero height**: 100vh on desktop, 80vh on mobile (short devices)
- **Typography scale**: 24px body → 16px on mobile
- **Touch targets**: Minimum 44x44px for buttons
- **Image optimization**: Use Next.js Image component with `priority` on hero

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] SEO meta tags implemented in `layout.tsx`
- [ ] Schema markup added to `page.tsx`
- [ ] Images optimized (WebP format, lazy loading)
- [ ] All sections responsive tested (mobile, tablet, desktop)
- [ ] Accessibility checked (color contrast, keyboard nav, alt text)
- [ ] CTA buttons link to `/record` page
- [ ] Analytics tracking added (if needed)
- [ ] Sitemap generated
- [ ] Open Graph images created
- [ ] Performance audit passed (Lighthouse 90+)

