'use client';

import React from 'react';

interface SparklineChartProps {
  data: number[];
  color?: string;
  height?: number;
  type?: 'line' | 'bar';
}

export function SparklineChart({ data, color = '#10B981', height = 36, type = 'line' }: SparklineChartProps) {
  if (!data || data.length === 0) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  if (type === 'bar') {
    return (
      <div className="flex items-end gap-1" style={{ height: `${height}px` }}>
        {data.map((val, i) => {
          const pct = Math.max(15, ((val - min) / range) * 100);
          return (
            <div
              key={i}
              className="flex-1 rounded-xs transition-all duration-300"
              style={{
                height: `${pct}%`,
                backgroundColor: color,
                opacity: i === data.length - 1 ? 1 : 0.4 + (i / data.length) * 0.5
              }}
            />
          );
        })}
      </div>
    );
  }

  // Line SVG Sparkline
  const width = 120;
  const padding = 4;
  const points = data
    .map((val, idx) => {
      const x = (idx / (data.length - 1)) * (width - padding * 2) + padding;
      const y = height - padding - ((val - min) / range) * (height - padding * 2);
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
      {/* End pulse dot */}
      {data.length > 0 && (() => {
        const lastVal = data[data.length - 1];
        const lastX = width - padding;
        const lastY = height - padding - ((lastVal - min) / range) * (height - padding * 2);
        return (
          <circle
            cx={lastX}
            cy={lastY}
            r="3"
            fill={color}
            className="animate-ping"
          />
        );
      })()}
    </svg>
  );
}
