import React from 'react';

export default function Badge({ children, variant = 'neutral', size = 'sm' }) {
  const variants = {
    allowed: 'bg-status-allowed/15 border-status-allowed/40 text-status-allowed',
    success: 'bg-status-allowed/15 border-status-allowed/40 text-status-allowed',
    rejected: 'bg-status-rejected/15 border-status-rejected/40 text-status-rejected',
    danger: 'bg-status-rejected/15 border-status-rejected/40 text-status-rejected',
    crimson: 'bg-crimson-600/15 border-crimson-600/40 text-crimson-400',
    warning: 'bg-status-warning/15 border-status-warning/40 text-status-warning',
    amber: 'bg-status-warning/15 border-status-warning/40 text-status-warning',
    neutral: 'bg-graphite-800 border-graphite-700 text-slate-300',
  };

  const sizes = {
    xs: 'text-[9px] px-2 py-0.5 tracking-wider',
    sm: 'text-[11px] px-2.5 py-1 tracking-wider',
    md: 'text-xs px-3 py-1.5 tracking-wider',
  };

  return (
    <span className={`inline-flex items-center font-mono font-bold rounded-lg border uppercase ${variants[variant] || variants.neutral} ${sizes[size]}`}>
      {children}
    </span>
  );
}
