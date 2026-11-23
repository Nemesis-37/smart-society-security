import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from 'lucide-react';

export default function Alert({ type = 'info', message, onClose }) {
  if (!message) return null;

  const styles = {
    success: {
      bg: 'bg-status-allowed/10 border-status-allowed/30 text-emerald-300',
      icon: <CheckCircle2 className="w-5 h-5 text-status-allowed shrink-0" />,
    },
    error: {
      bg: 'bg-status-rejected/10 border-status-rejected/30 text-rose-300',
      icon: <XCircle className="w-5 h-5 text-status-rejected shrink-0" />,
    },
    warning: {
      bg: 'bg-status-warning/10 border-status-warning/30 text-amber-300',
      icon: <AlertTriangle className="w-5 h-5 text-status-warning shrink-0" />,
    },
    info: {
      bg: 'bg-graphite-850 border-graphite-700 text-slate-300',
      icon: <Info className="w-5 h-5 text-slate-400 shrink-0" />,
    },
  }[type] || {
    bg: 'bg-graphite-850 border-graphite-700 text-slate-300',
    icon: <Info className="w-5 h-5 text-slate-400 shrink-0" />,
  };

  return (
    <div className={`p-4 rounded-xl border flex items-start space-x-3 text-xs md:text-sm animate-fadeIn ${styles.bg}`}>
      {styles.icon}
      <div className="flex-1 font-medium leading-relaxed font-sans">
        {message}
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="p-1 rounded-md text-slate-400 hover:text-white transition-colors"
        >
          <X size={15} />
        </button>
      )}
    </div>
  );
}
