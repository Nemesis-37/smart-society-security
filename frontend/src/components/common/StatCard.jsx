import React from 'react';

export default function StatCard({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  trend,
  color = 'blue' 
}) {
  const colorStyles = {
    blue: {
      bg: 'bg-blue-600/10',
      border: 'border-blue-500/20 hover:border-blue-500/40',
      icon: 'text-blue-400',
      glow: 'group-hover:shadow-blue-500/10'
    },
    emerald: {
      bg: 'bg-emerald-600/10',
      border: 'border-emerald-500/20 hover:border-emerald-500/40',
      icon: 'text-emerald-400',
      glow: 'group-hover:shadow-emerald-500/10'
    },
    rose: {
      bg: 'bg-rose-600/10',
      border: 'border-rose-500/20 hover:border-rose-500/40',
      icon: 'text-rose-400',
      glow: 'group-hover:shadow-rose-500/10'
    },
    cyan: {
      bg: 'bg-cyan-600/10',
      border: 'border-cyan-500/20 hover:border-cyan-500/40',
      icon: 'text-cyan-400',
      glow: 'group-hover:shadow-cyan-500/10'
    },
  }[color] || colorStyles.blue;

  return (
    <div className={`p-5 rounded-2xl bg-navy-900/80 border ${colorStyles.border} shadow-lg transition-all duration-300 group hover:-translate-y-0.5 ${colorStyles.glow}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        {Icon && (
          <div className={`p-2.5 rounded-xl ${colorStyles.bg} ${colorStyles.icon} transition-transform group-hover:scale-110`}>
            <Icon size={20} />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline justify-between">
        <span className="text-2xl md:text-3xl font-extrabold tracking-tight text-white font-mono">
          {value}
        </span>
        {trend && (
          <span className="text-xs font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
            {trend}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-1 text-xs text-slate-400">
          {subtitle}
        </p>
      )}
    </div>
  );
}
