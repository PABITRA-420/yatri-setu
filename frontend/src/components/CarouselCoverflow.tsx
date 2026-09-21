"use client";

import { motion } from "framer-motion";
import { ChevronLeftIcon, ChevronRightIcon } from "lucide-react";
import React from "react";
import {
  Autoplay,
  EffectCoverflow,
  Navigation,
  Pagination,
} from "swiper/modules";
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/effect-coverflow";
import "swiper/css/pagination";
import "swiper/css/navigation";

import { cn } from "@/lib/utils";

export interface CarouselSlideItem {
  src: string;
  alt: string;
  title?: string;
  subtitle?: string;
  badge?: string;
}

interface CarouselCoverflowProps {
  images?: CarouselSlideItem[];
  className?: string;
  showPagination?: boolean;
  showNavigation?: boolean;
  loop?: boolean;
  autoplay?: boolean;
  spaceBetween?: number;
}

export const CarouselCoverflow: React.FC<CarouselCoverflowProps> = ({
  images = [
    {
      src: "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=800&q=80",
      alt: "Darjeeling Ridge Control Center",
      title: "Darjeeling Telemetry Desk",
      subtitle: "Mall Road & Tiger Hill Flow Monitoring",
      badge: "Active Node"
    },
    {
      src: "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=800&q=80",
      alt: "Kalimpong Regional Coordination Office",
      title: "Kalimpong Liaison Hub",
      subtitle: "Alternative Route & Homestay Coordination",
      badge: "Sanctuary Desk"
    },
    {
      src: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80",
      alt: "Rishop High Altitude Safety Outpost",
      title: "Rishop Alpine Watch",
      subtitle: "360° Weather & Ridge Transit Guides",
      badge: "High Altitude"
    },
    {
      src: "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80",
      alt: "Lava Neora Forest Gate Post",
      title: "Neora Valley Forest Post",
      subtitle: "Permits & Ecological Capacity Checkpoints",
      badge: "Eco Desk"
    },
    {
      src: "https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=800&q=80",
      alt: "Mirik Lake Transit & Volunteer Station",
      title: "Mirik Lake Operations",
      subtitle: "Yatri Mitra Volunteer Network Hub",
      badge: "Emergency 24/7"
    },
    {
      src: "https://images.unsplash.com/photo-1587061949409-02df41d5e562?auto=format&fit=crop&w=800&q=80",
      alt: "Gram Panchayat Homestay Registry",
      title: "Panchayat Verification Desk",
      subtitle: "Host Onboarding & Direct Payout Support",
      badge: "Verified Stays"
    }
  ],
  className,
  showPagination = true,
  showNavigation = true,
  loop = true,
  autoplay = true,
  spaceBetween = 32,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, translateY: 20 }}
      animate={{ opacity: 1, translateY: 0 }}
      transition={{
        duration: 0.4,
        delay: 0.2,
      }}
      className={cn("w-full max-w-5xl mx-auto relative px-2 sm:px-6", className)}
    >
      <style>{`
        .coverflow-carousel .swiper-pagination-bullet {
          background: #d97706 !important;
          opacity: 0.4;
          width: 8px;
          height: 8px;
          transition: all 0.3s ease;
        }
        .coverflow-carousel .swiper-pagination-bullet-active {
          opacity: 1;
          width: 24px;
          border-radius: 9999px;
          background: #f59e0b !important;
        }
        .coverflow-carousel .swiper-button-prev,
        .coverflow-carousel .swiper-button-next {
          width: 44px;
          height: 44px;
          border-radius: 9999px;
          background: rgba(15, 23, 42, 0.75);
          backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.15);
          color: #ffffff;
          box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
          transition: all 0.2s ease;
        }
        .coverflow-carousel .swiper-button-prev:hover,
        .coverflow-carousel .swiper-button-next:hover {
          background: rgba(217, 119, 6, 0.9);
          border-color: rgba(245, 158, 11, 0.5);
          transform: scale(1.05);
        }
        .coverflow-carousel .swiper-button-prev:after,
        .coverflow-carousel .swiper-button-next:after {
          display: none;
        }
      `}</style>

      <Swiper
        spaceBetween={spaceBetween}
        autoplay={
          autoplay
            ? {
                delay: 2600,
                disableOnInteraction: false,
                pauseOnMouseEnter: true,
              }
            : false
        }
        effect="coverflow"
        grabCursor={true}
        centeredSlides={true}
        loop={loop}
        breakpoints={{
          320: {
            slidesPerView: 1.25,
            spaceBetween: 16,
          },
          640: {
            slidesPerView: 1.8,
            spaceBetween: 24,
          },
          1024: {
            slidesPerView: 2.35,
            spaceBetween: 32,
          },
        }}
        coverflowEffect={{
          rotate: 0,
          slideShadows: false,
          stretch: 0,
          depth: 120,
          modifier: 2.2,
        }}
        pagination={
          showPagination
            ? {
                clickable: true,
              }
            : false
        }
        navigation={
          showNavigation
            ? {
                nextEl: ".coverflow-next",
                prevEl: ".coverflow-prev",
              }
            : false
        }
        className="coverflow-carousel pb-14 pt-4"
        modules={[EffectCoverflow, Autoplay, Pagination, Navigation]}
      >
        {images.map((item, index) => (
          <SwiperSlide
            key={index}
            className="!h-[360px] sm:!h-[400px] w-full rounded-3xl overflow-hidden shadow-2xl border border-white/15 relative group select-none"
          >
            <img
              className="h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-105"
              src={item.src}
              alt={item.alt}
            />
            {/* Multi-tone gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-stone-950 via-stone-950/40 to-transparent" />

            {/* Slide Metadata */}
            <div className="absolute bottom-0 inset-x-0 p-6 sm:p-7 z-10 space-y-2.5">
              {item.badge && (
                <span className="inline-block px-3.5 py-1.5 rounded-full bg-amber-500/25 backdrop-blur-md border border-amber-400/50 text-amber-300 text-xs sm:text-sm font-mono font-bold tracking-wide">
                  {item.badge}
                </span>
              )}
              {item.title && (
                <h3 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                  {item.title}
                </h3>
              )}
              {item.subtitle && (
                <p className="text-sm sm:text-base text-stone-200 font-medium leading-normal">
                  {item.subtitle}
                </p>
              )}
            </div>
          </SwiperSlide>
        ))}

        {showNavigation && (
          <>
            <button
              aria-label="Previous Slide"
              className="coverflow-prev swiper-button-prev !left-1 sm:!left-3 !top-1/2 -translate-y-1/2 flex items-center justify-center cursor-pointer"
            >
              <ChevronLeftIcon className="h-5 w-5 text-white" />
            </button>
            <button
              aria-label="Next Slide"
              className="coverflow-next swiper-button-next !right-1 sm:!right-3 !top-1/2 -translate-y-1/2 flex items-center justify-center cursor-pointer"
            >
              <ChevronRightIcon className="h-5 w-5 text-white" />
            </button>
          </>
        )}
      </Swiper>
    </motion.div>
  );
};

export default CarouselCoverflow;
