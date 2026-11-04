import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { Toaster } from 'sonner';

import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Aasirbad — Preserve your family\'s voice',
  description:
    'Preserve the voices of the people you love. Record once, and let AI speak in their voice for generations.',
  keywords: ['voice cloning', 'AI voice', 'family voice', 'aasirbad'],
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
