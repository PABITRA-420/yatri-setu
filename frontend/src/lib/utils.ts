import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { CrowdLevel } from '@/types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getCrowdBadgeStyle(level: CrowdLevel): { bg: string; text: string; border: string; label: string; dot: string } {
  switch (level) {
    case 'LOW':
      return {
        bg: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
        text: 'text-emerald-600 dark:text-emerald-400',
        border: 'border-emerald-500/30',
        label: 'Low Crowd',
        dot: 'bg-emerald-500'
      };
    case 'MEDIUM':
      return {
        bg: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
        text: 'text-amber-600 dark:text-amber-400',
        border: 'border-amber-500/30',
        label: 'Moderate Footfall',
        dot: 'bg-amber-500'
      };
    case 'HIGH':
      return {
        bg: 'bg-orange-500/10 text-orange-600 dark:text-orange-400',
        text: 'text-orange-600 dark:text-orange-400',
        border: 'border-orange-500/30',
        label: 'High Density',
        dot: 'bg-orange-500'
      };
    case 'VERY HIGH':
      return {
        bg: 'bg-rose-500/10 text-rose-600 dark:text-rose-400',
        text: 'text-rose-600 dark:text-rose-400',
        border: 'border-rose-500/30',
        label: 'Severe Congestion',
        dot: 'bg-rose-500 animate-pulse'
      };
    default:
      return {
        bg: 'bg-slate-500/10 text-slate-600',
        text: 'text-slate-600',
        border: 'border-slate-500/30',
        label: 'Unknown',
        dot: 'bg-slate-400'
      };
  }
}

export function formatINR(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
}
