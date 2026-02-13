import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { Toaster } from 'sonner';

import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'आसिर्बाद — परिवारको आवाज सुरक्षित राख्नुहोस्',
  description:
    'हजुरबुवा-हजुरआमाको कथा, आमाबुवाको आसिर्बाद — AI ले तपाईंको प्रियजनको आवाज जोगाएर राख्छ।',
  keywords: ['voice cloning', 'nepali voice', 'AI voice', 'family voice', 'आसिर्बाद', 'नेपाली'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Toaster richColors position="top-right" />
        {children}
      </body>
    </html>
  );
}
