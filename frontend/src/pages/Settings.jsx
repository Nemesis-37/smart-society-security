import React from 'react';
import { Settings as SettingsIcon, Cpu, Database, Video, ShieldCheck, Terminal } from 'lucide-react';
import Badge from '../components/common/Badge';

export default function Settings() {
  return (
    <div className="space-y-6 animate-fadeIn max-w-4xl">
      {/* Header */}
      <div className="pb-4 border-b border-navy-800">
        <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2">
          <SettingsIcon className="w-6 h-6 text-slate-400" />
          <span>System Settings & Configuration</span>
        </h2>
        <p className="text-xs md:text-sm text-slate-400 mt-1">
          Hardware bindings, algorithm hyperparameters, and storage configuration
        </p>
      </div>

      {/* Settings Grid */}
      <div className="space-y-4">
        {/* Core Algorithm Parameters */}
        <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            <span>Facial Recognition Pipeline Hyperparameters</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div className="p-3.5 rounded-xl bg-navy-950 border border-navy-800 flex justify-between items-center">
              <span className="text-slate-400">Default Match Threshold:</span>
              <span className="text-white font-bold">0.50 (Euclidean)</span>
            </div>
            <div className="p-3.5 rounded-xl bg-navy-950 border border-navy-800 flex justify-between items-center">
              <span className="text-slate-400">Canonical ROI Resolution:</span>
              <span className="text-white font-bold">100 × 100 px</span>
            </div>
            <div className="p-3.5 rounded-xl bg-navy-950 border border-navy-800 flex justify-between items-center">
              <span className="text-slate-400">CLAHE Clip Limit / Tile:</span>
              <span className="text-white font-bold">2.0 / 8 × 8</span>
            </div>
            <div className="p-3.5 rounded-xl bg-navy-950 border border-navy-800 flex justify-between items-center">
              <span className="text-slate-400">HOG Vector Dimensions:</span>
              <span className="text-cyan-400 font-bold">128-D Float32</span>
            </div>
          </div>
        </div>

        {/* Database & Storage */}
        <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Database className="w-4 h-4 text-emerald-400" />
            <span>Database & Storage Architecture</span>
          </h3>

          <div className="space-y-2.5 text-xs">
            <div className="p-3.5 rounded-xl bg-navy-950 border border-navy-800 flex justify-between items-center font-mono">
              <span className="text-slate-400">SQLite Database Path:</span>
              <span className="text-slate-200">database/society_security.db</span>
            </div>
            <div className="p-3.5 rounded-xl bg-navy-950 border border-navy-800 flex justify-between items-center font-mono">
              <span className="text-slate-400">Resident Photo Directory:</span>
              <span className="text-slate-200">dataset/residents/</span>
            </div>
            <div className="p-3.5 rounded-xl bg-navy-950 border border-navy-800 flex justify-between items-center font-mono">
              <span className="text-slate-400">Binary Serialization:</span>
              <span className="text-emerald-400 font-bold">tobytes() / frombuffer()</span>
            </div>
          </div>
        </div>

        {/* System & Camera Bindings */}
        <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Video className="w-4 h-4 text-cyan-400" />
            <span>Optical Input Bindings</span>
          </h3>

          <div className="p-4 rounded-xl bg-navy-950 border border-navy-800 text-xs text-slate-300 space-y-2">
            <p>
              Camera device index defaults to <code>0</code> with automatic fallback to <code>1</code>.
            </p>
            <p className="text-slate-400 text-[11px]">
              DirectShow driver: <code>cv2.CAP_DSHOW</code> enabled on Windows platforms for low latency frame acquisition.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
