'use client';

import React from 'react';

interface PriceProximityBarProps {
  buyPrice: number;
  sellPrice: number;
  currentPrice: number;
}

export const PriceProximityBar: React.FC<PriceProximityBarProps> = ({
  buyPrice,
  sellPrice,
  currentPrice,
}) => {
  // Calculate position as percentage (0-100%)
  const position = Math.max(
    0,
    Math.min(100, ((currentPrice - buyPrice) / (sellPrice - buyPrice)) * 100)
  );

  // Calculate gradient fill width based on position
  const gradientWidth = position;

  return (
    <div className="relative w-full h-[50px] flex items-end pb-2">
      {/* Moving Price Tag */}
      <div
        className="absolute top-0 z-10 transition-all duration-500 ease-[cubic-bezier(0.4,0,0.2,1)]"
        style={{ left: `${position}%`, transform: 'translateX(-50%)' }}
      >
        <div className="relative bg-slate-200 dark:bg-zinc-800 border border-slate-300 dark:border-zinc-700 px-3 py-1.5 rounded-md shadow-lg">
          <span className="text-slate-900 dark:text-white font-bold text-sm whitespace-nowrap">
            {currentPrice.toFixed(2)}
          </span>
          {/* Triangle Pointer */}
          <div
            className="absolute left-1/2 -bottom-[6px] -translate-x-1/2 w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[6px] border-t-slate-200 dark:border-t-zinc-800"
          />
        </div>
      </div>

      {/* Progress Bar */}
      <div className="relative w-full h-[10px] bg-slate-300 dark:bg-zinc-900 rounded-[5px] overflow-hidden shadow-[inset_0_2px_4px_rgba(0,0,0,0.15)] dark:shadow-[inset_0_2px_4px_rgba(0,0,0,0.3)]">
        {/* Gradient Fill */}
        <div
          className="absolute top-0 left-0 h-full transition-all duration-300"
          style={{
            width: `${gradientWidth}%`,
            background: 'linear-gradient(to right, #4caf50 0%, #ffeb3b 50%, #f44336 100%)',
          }}
        />
      </div>
    </div>
  );
};
