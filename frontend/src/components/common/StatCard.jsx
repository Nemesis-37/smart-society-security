import React from 'react';

export default function StatCard({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  trend,
  color = 'crimson' 
}) {
  const colorStyles = {
    crimson: {
      bg: 'bg-crimson-600/10 border-crimson-600/30 text-crimson-500',
      borderHover: 'hover:border-crimson-600/50',
      badge: 'text-crimson-400 bg-crimson-600/10 border-crimson-600/30',
    },
    allowed: {
      bg: 'bg-status-allowed/10 border-status-allowed/30 text-status-allowed',
      borderHover: 'hover:border-status-allowed/50',
      badge: 'text-status-allowed bg-status-allowed/10 border-status-allowed/30',
    },
    amber: {
      bg: 'bg-status-warning/10 border-status-warning/30 text-status-warning',
      borderHover: 'hover:border-status-warning/50',
      badge: 'text-status-warning bg-status-warning/10 border-status-warning/30',
    },
    neutral: {
      bg: 'bg-graphite-800 border-graphite-700 text-slate-300',
      borderHover: 'hover:border-graphite-600',
      badge: 'text-slate-300 bg-graphite-800 border-graphite-700',
    },
  }[color] || {
    bg: 'bg-crimson-600/10 border-crimson-600/30 text-crimson-500',
    borderHover: 'hover:border-crimson-600/50',
    badge: 'text-crimson-400 bg-crimson-600/10 border-crimson-600/30',
  };

  return (
    <div className={`p-5 rounded-2xl bg-graphite-900 border border-graphite-800 transition-all duration-300 group hover:-translate-y-0.5 ${colorStyles.borderHover} shadow-lg shadow-black/40`}>
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono">
          {title}
        </span>
        {Icon && (
          <div className={`p-2.5 rounded-xl border ${colorStyles.bg} transition-transform group-hover:scale-110`}>
            <Icon size={18} />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline justify-between">
        <span className="text-2xl md:text-3xl font-extrabold tracking-tight text-white font-mono">
          {value}
        </span>
        {trend && (
          <span className={`text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${colorStyles.badge}`}>
            {trend}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-1 text-xs text-slate-400 font-medium">
          {subtitle}
        </p>
      )}
    </div>
  );
}
