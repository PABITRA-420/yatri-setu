import type { Metadata } from 'next';
import { Plus_Jakarta_Sans, Cormorant_Garamond } from 'next/font/google';
import './globals.css';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { SmoothScrollProvider } from '@/components/SmoothScrollProvider';
import { cn } from "@/lib/utils";

const sansFont = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
  weight: ['400', '500', '600', '700', '800']
});

const editorialFont = Cormorant_Garamond({
  subsets: ['latin'],
  variable: '--font-serif',
  display: 'swap',
  style: ['normal', 'italic'],
  weight: ['400', '500', '600', '700']
});

export const metadata: Metadata = {
  title: 'Yatri Setu | Himalayan Flow Intelligence & Hyperlocal Tourism',
  description:
    'Active tourist flow management, explainable crowd scoring, and rural homestays with built-in traveler safety.',
  keywords: [
    'Yatri Setu',
    'Overtourism Management',
    'Rural Tourism',
    'Himalayan Homestays',
    'Crowd Prediction',
    'Traveler Safety'
  ]
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={cn("h-full", "antialiased", editorialFont.variable, sansFont.variable)}>
      <body className="min-h-full flex flex-col bg-[#F6F4F0] text-stone-900 dark:bg-[#0C0F14] dark:text-stone-100 transition-colors font-sans selection:bg-amber-500/20 selection:text-amber-900 dark:selection:text-amber-200">
        <SmoothScrollProvider>
          <Navbar />
          <main className="flex-1">{children}</main>
          <Footer />
        </SmoothScrollProvider>
      </body>
    </html>
  );
}
