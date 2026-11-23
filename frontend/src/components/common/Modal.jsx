import React from 'react';
import { X } from 'lucide-react';

export default function Modal({ isOpen, onClose, title, children, maxWidth = 'max-w-lg' }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-sm animate-fadeIn">
      <div 
        className={`w-full ${maxWidth} rounded-2xl bg-graphite-900 border border-graphite-700 shadow-2xl p-6 relative overflow-hidden`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between pb-4 border-b border-graphite-800">
          <h3 className="text-base font-extrabold text-white tracking-wide font-mono uppercase flex items-center space-x-2">
            <span className="w-1.5 h-3.5 bg-crimson-600 inline-block rounded-xs" />
            <span>{title}</span>
          </h3>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-graphite-800 transition-colors"
          >
            <X size={18} />
          </button>
        </div>
        <div className="mt-4">
          {children}
        </div>
      </div>
    </div>
  );
}
