import React from 'react';

export default function Badge({ children, variant = 'neutral', size = 'sm' }) {
  const variants = {
    success: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400',
    danger: 'bg-rose-500/15 border-rose-500/30 text-rose-400',
    warning: 'bg-amber-500/15 border-amber-500/30 text-amber-400',
    info: 'bg-blue-500/15 border-blue-500/30 text-blue-400',
    cyan: 'bg-cyan-500/15 border-cyan-500/30 text-cyan-400',
    neutral: 'bg-slate-700/30 border-slate-700 text-slate-300',
  };

  const sizes = {
    xs: 'text-[10px] px-2 py-0.5',
    sm: 'text-xs px-2.5 py-1',
    md: 'text-sm px-3 py-1.5',
  };

  return (
    <span className={`inline-flex items-center font-semibold rounded-lg border uppercase tracking-wider ${variants[variant] || variants.neutral} ${sizes[size]}`}>
      {children}
    </span>
  );
}
