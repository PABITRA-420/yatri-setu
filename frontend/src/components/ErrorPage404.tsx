'use client';

import React from "react";

interface ErrorPage404Props {
  onGoHome?: () => void;
}

export default function ErrorPage404({ onGoHome }: ErrorPage404Props) {
  const handleGoHome = () => {
    if (onGoHome) {
      onGoHome();
    } else {
      window.location.href = "/";
    }
  };

  const fontRounded = "'Baloo 2', ui-rounded, system-ui, sans-serif";
  const fontDisplay = '"Helvetica Neue", Arial, sans-serif';

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black px-6 text-center">
      {/* Load the rounded display font used for headline/body/button */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&display=swap');
      `}</style>

      {/* Glowing blurred code */}
      <div
        className="relative select-none leading-none"
        style={{ fontFamily: fontDisplay }}
      >
        {/* Ambient glow layer */}
        <span
          aria-hidden="true"
          className="absolute inset-0 block text-[7rem] font-black tracking-tight text-white opacity-90 blur-3xl sm:text-[10rem] md:text-[13rem]"
        >
          404
        </span>
        {/* Sharp layer, faded out at the top so it reads as glow-to-solid */}
        <span
          className="relative block text-[7rem] font-black tracking-tight text-white sm:text-[10rem] md:text-[13rem]"
          style={{
            WebkitMaskImage:
              "linear-gradient(to bottom, transparent 0%, black 55%)",
            maskImage: "linear-gradient(to bottom, transparent 0%, black 55%)",
          }}
        >
          404
        </span>
      </div>

      {/* Heading */}
      <h1
        className="mt-6 text-xl font-extrabold text-white sm:text-2xl md:text-3xl"
        style={{ fontFamily: fontRounded }}
      >
        The page you requested cannot be found.
      </h1>

      {/* Subtext */}
      <p
        className="mt-4 max-w-md text-sm font-medium text-gray-400 sm:text-base"
        style={{ fontFamily: fontRounded }}
      >
        The link may be broken, or the page could have been taken down or
        renamed.
      </p>

      {/* Button */}
      <button
        onClick={handleGoHome}
        style={{ fontFamily: fontRounded }}
        className="mt-8 rounded-full bg-white px-6 py-3 text-sm font-semibold text-black transition-colors hover:bg-gray-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-black cursor-pointer"
      >
        Go back home
      </button>
    </div>
  );
}
