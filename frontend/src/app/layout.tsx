import type { Metadata } from 'next';
import { Plus_Jakarta_Sans, Cormorant_Garamond } from 'next/font/google';
import './globals.css';
import { Navbar } from '@/components/Navbar';
import { TopMarquee } from '@/components/TopMarquee';
import { Footer } from '@/components/Footer';
import { SmoothScrollProvider } from '@/components/SmoothScrollProvider';

const sansFont = Plus_Jakarta_Sans({ subsets: ['latin'], variable: '--font-sans', display: 'swap', weight: ['400','500','600','700','800'] });
const editorialFont = Cormorant_Garamond({ subsets: ['latin'], variable: '--font-serif', display: 'swap', style: ['normal','italic'], weight: ['400','500','600','700'] });

export const metadata: Metadata = {
  title: 'Yatri Setu | Intelligent Travel',
  description: 'Discover quieter destinations, local stays and intelligent travel planning with Yatri Setu.'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sansFont.variable} ${editorialFont.variable}`}>
      <body className="min-h-screen bg-[#F5F2EA] text-[#171714] font-sans">
        <SmoothScrollProvider>
          <Navbar />
          <TopMarquee />
          <main className="min-h-screen">{children}</main>
          <Footer />
        </SmoothScrollProvider>
      </body>
    </html>
  );
}
