import type { Metadata } from 'next';
import './globals.css';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';

export const metadata: Metadata = {
  title: 'Yatri Setu | Smart Crowd & Alternate-Destination Hyperlocal Tourism (SIH 2026)',
  description:
    'Active tourist flow management, explainable crowd scoring, and rural homestays with built-in traveler safety for the Smart India Hackathon 2026.',
  keywords: [
    'Smart India Hackathon 2026',
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
    <html lang="en" className="h-full antialiased scroll-smooth">
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 transition-colors">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
