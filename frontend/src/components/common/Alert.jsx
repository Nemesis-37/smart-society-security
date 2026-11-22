import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from 'lucide-react';

export default function Alert({ type = 'info', message, onClose }) {
  if (!message) return null;

  const styles = {
    success: {
      bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300',
      icon: <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />,
    },
    error: {
      bg: 'bg-rose-500/10 border-rose-500/30 text-rose-300',
      icon: <XCircle className="w-5 h-5 text-rose-400 shrink-0" />,
    },
    warning: {
      bg: 'bg-amber-500/10 border-amber-500/30 text-amber-300',
      icon: <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />,
    },
    info: {
      bg: 'bg-blue-500/10 border-blue-500/30 text-blue-300',
      icon: <Info className="w-5 h-5 text-blue-400 shrink-0" />,
    },
  }[type] || styles.info;

  return (
    <div className={`p-4 rounded-xl border flex items-start space-x-3 text-sm animate-fadeIn ${styles.bg}`}>
      {styles.icon}
      <div className="flex-1 font-medium leading-relaxed">
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
