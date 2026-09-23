'use client';

import React, { useRef } from 'react';
import { motion, useInView } from 'motion/react';

interface TextRevealProps {
  text: string;
  className?: string;
  delay?: number;
  mode?: 'words' | 'characters';
}

export function TextReveal({
  text,
  className = '',
  delay = 0,
  mode = 'words'
}: TextRevealProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });

  if (mode === 'characters') {
    const characters = text.split('');
    return (
      <div ref={ref} className={`inline-flex flex-wrap overflow-hidden ${className}`}>
        {characters.map((char, index) => (
          <motion.span
            key={index}
            initial={{ opacity: 0, y: '80%' }}
            animate={isInView ? { opacity: 1, y: '0%' } : { opacity: 0, y: '80%' }}
            transition={{
              duration: 0.4,
              delay: delay + index * 0.02,
              ease: [0.22, 1, 0.36, 1]
            }}
            className="inline-block"
          >
            {char === ' ' ? '\u00A0' : char}
          </motion.span>
        ))}
      </div>
    );
  }

  const words = text.split(' ');
  return (
    <div ref={ref} className={`flex flex-wrap gap-x-1.5 gap-y-1 overflow-hidden ${className}`}>
      {words.map((word, index) => (
        <motion.span
          key={index}
          initial={{ opacity: 0, y: '60%' }}
          animate={isInView ? { opacity: 1, y: '0%' } : { opacity: 0, y: '60%' }}
          transition={{
            duration: 0.5,
            delay: delay + index * 0.05,
            ease: [0.22, 1, 0.36, 1]
          }}
          className="inline-block"
        >
          {word}
        </motion.span>
      ))}
    </div>
  );
}
