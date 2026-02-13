'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Mic, Sparkles, Heart, ArrowRight, Users, Shield, Volume2 } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50/50 via-white to-orange-50/30">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-md shadow-amber-500/20">
            <span className="text-white text-lg font-bold">ॐ</span>
          </div>
          <div className="flex flex-col leading-tight">
            <span className="text-xl font-bold text-gray-900 tracking-tight">आसिर्बाद</span>
            <span className="text-[10px] text-amber-700 font-medium -mt-0.5">AASIRBAD</span>
          </div>
        </Link>
        <div className="flex items-center gap-4">
          <Link
            href="/login"
            className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="text-sm font-medium bg-gradient-to-r from-amber-500 to-orange-600 text-white px-5 py-2 rounded-lg hover:from-amber-600 hover:to-orange-700 transition-all shadow-md shadow-amber-500/20"
          >
            सुरु गर्नुहोस्
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 pt-16 pb-32">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-4xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-full px-4 py-1.5 mb-8">
            <span className="text-amber-600 text-sm">🙏</span>
            <span className="text-sm font-medium text-amber-800">
              परिवारको आवाज सुरक्षित राख्नुहोस्
            </span>
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 leading-tight tracking-tight">
            परिवारको <span className="text-amber-600">आवाज</span>
            <br />
            <span className="text-orange-600">सदाको लागि</span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            हजुरबुवा-हजुरआमाको कथा, आमाबुवाको आसिर्बाद, परिवारको माया —
            <br className="hidden sm:block" />
            AI प्रविधिले तपाईंको प्रियजनको आवाज जोगाएर राख्छ।
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/register"
              className="flex items-center gap-2 bg-gradient-to-r from-amber-500 to-orange-600 text-white px-8 py-3.5 rounded-xl hover:from-amber-600 hover:to-orange-700 transition-all text-lg font-medium shadow-lg shadow-amber-500/25 hover:shadow-xl"
            >
              आवाज सुरक्षित गर्नुहोस्
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="#how-it-works"
              className="flex items-center gap-2 text-gray-700 px-8 py-3.5 rounded-xl border border-gray-200 hover:border-amber-300 hover:bg-amber-50 transition-all text-lg font-medium"
            >
              <Volume2 className="w-5 h-5" />
              कसरी काम गर्छ?
            </Link>
          </div>
        </motion.div>

        {/* Cultural divider */}
        <div className="flex items-center justify-center gap-3 mt-24 mb-16">
          <div className="h-px w-16 bg-gradient-to-r from-transparent to-amber-300" />
          <span className="text-amber-400 text-2xl">✦</span>
          <div className="h-px w-16 bg-gradient-to-l from-transparent to-amber-300" />
        </div>

        {/* Why Aasirbad */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="max-w-3xl mx-auto text-center mb-20"
        >
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">
            किन <span className="text-amber-600">आसिर्बाद</span>?
          </h2>
          <p className="text-gray-600 text-lg leading-relaxed">
            नेपाली परिवारमा आवाज नै आसिर्बाद हो। हजुरबुवाले सुनाउनुभएको कथा,
            आमाले गाउनुभएको लोरी, बुवाले दिनुभएको सल्लाह — यी सबै अनमोल छन्।
            आसिर्बादले यी आवाजहरू AI को शक्तिले सुरक्षित राख्छ।
          </p>
        </motion.div>

        {/* How It Works */}
        <motion.div
          id="how-it-works"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <h2 className="text-center text-3xl font-bold text-gray-900 mb-16">
            कसरी काम गर्छ?
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Mic,
                step: '०१',
                title: 'आवाज रेकर्ड गर्नुहोस्',
                description:
                  'लिंक पठाउनुहोस् — आमा, बुवा वा प्रियजनले आफ्नो मोबाइलबाटै नेपालीमा बोलेर रेकर्ड गर्न सक्छन्। कुनै स्क्रिप्ट चाहिँदैन।',
              },
              {
                icon: Sparkles,
                step: '०२',
                title: 'AI ले सिक्छ',
                description:
                  'हाम्रो AI ले आवाजको हरेक विशेषता — लय, स्वर, भावना — बुझ्छ र एउटा अनौठो भ्वाइस मोडेल बनाउँछ।',
              },
              {
                icon: Heart,
                step: '०३',
                title: 'आवाज जीवित रहन्छ',
                description:
                  'कुनै पनि पाठ टाइप गर्नुहोस् र आफ्नो प्रियजनको आवाजमा सुन्नुहोस्। कथा, आसिर्बाद, सन्देश — जे होस्।',
              },
            ].map((item) => (
              <div
                key={item.step}
                className="relative bg-white rounded-2xl p-8 border border-amber-100 shadow-sm hover:shadow-md hover:border-amber-200 transition-all"
              >
                <span className="text-6xl font-bold text-amber-100 absolute top-4 right-6">
                  {item.step}
                </span>
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-50 to-orange-50 flex items-center justify-center mb-4 border border-amber-100">
                  <item.icon className="w-6 h-6 text-amber-600" />
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

        {/* Family Use Cases */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mt-32"
        >
          <h2 className="text-center text-3xl font-bold text-gray-900 mb-4">
            परिवारको हरेक पलको लागि
          </h2>
          <p className="text-center text-gray-600 mb-16 max-w-2xl mx-auto">
            आसिर्बादले तपाईंको परिवारको आवाजलाई सधैँको लागि सुरक्षित राख्छ
          </p>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: '🙏', title: 'हजुरबुवा-हजुरआमाको कथा', desc: 'बालबालिकालाई सुनाउन हजुरबुवा-हजुरआमाको आवाजमा कथा' },
              { icon: '💐', title: 'विवाह र पर्वको आसिर्बाद', desc: 'विशेष अवसरमा परिवारको आवाजमा शुभकामना र आसिर्बाद' },
              { icon: '📖', title: 'पारिवारिक इतिहास', desc: 'पुस्तौँ-पुस्ताको कथा आफ्नै परिवारको आवाजमा सुरक्षित' },
              { icon: '🎵', title: 'आमाको लोरी', desc: 'आमाले गाउनुभएको लोरी र भजन सधैँको लागि सुरक्षित' },
              { icon: '🛡️', title: 'सुरक्षित र निजी', desc: 'तपाईंको आवाज तपाईंकै हो — एन्क्रिप्टेड र सुरक्षित स्टोरेज' },
              { icon: '📱', title: 'जहाँबाट पनि', desc: 'मोबाइल वा कम्प्युटर — जहाँबाट पनि रेकर्ड र सुन्न सकिन्छ' },
            ].map((feature) => (
              <div
                key={feature.title}
                className="bg-white/80 backdrop-blur rounded-xl p-6 border border-amber-100 hover:border-amber-200 transition-all hover:shadow-sm"
              >
                <span className="text-2xl mb-3 block">{feature.icon}</span>
                <h4 className="font-semibold text-gray-900 mb-1">
                  {feature.title}
                </h4>
                <p className="text-sm text-gray-600">{feature.desc}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Trust section */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.7 }}
          className="mt-32 text-center"
        >
          <div className="inline-flex items-center gap-6 bg-white rounded-2xl border border-amber-100 px-8 py-5 shadow-sm">
            <div className="flex items-center gap-2 text-gray-600">
              <Shield className="w-5 h-5 text-amber-600" />
              <span className="text-sm font-medium">सुरक्षित</span>
            </div>
            <div className="w-px h-6 bg-gray-200" />
            <div className="flex items-center gap-2 text-gray-600">
              <Users className="w-5 h-5 text-amber-600" />
              <span className="text-sm font-medium">परिवार-केन्द्रित</span>
            </div>
            <div className="w-px h-6 bg-gray-200" />
            <div className="flex items-center gap-2 text-gray-600">
              <Heart className="w-5 h-5 text-amber-600" />
              <span className="text-sm font-medium">नेपालीमा</span>
            </div>
          </div>
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="border-t border-amber-100 py-8 bg-amber-50/30">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-amber-600 font-bold">ॐ</span>
            <span className="text-sm text-gray-500">
              &copy; 2026 आसिर्बाद (Aasirbad). सबै अधिकार सुरक्षित।
            </span>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-500">
            <a href="#" className="hover:text-amber-700">गोपनीयता</a>
            <a href="#" className="hover:text-amber-700">सर्तहरू</a>
            <a href="#" className="hover:text-amber-700">सम्पर्क</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
