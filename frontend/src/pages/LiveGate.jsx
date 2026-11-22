import React, { useState, useEffect } from 'react';
import { 
  Video, 
  ShieldCheck, 
  Sliders, 
  RefreshCw, 
  Camera, 
  AlertTriangle,
  Play,
  Square,
  Activity
} from 'lucide-react';
import Badge from '../components/common/Badge';
import Alert from '../components/common/Alert';
import { gateApi } from '../services/api';

export default function LiveGate() {
  const [gateConfig, setGateConfig] = useState({
    status: 'Ready',
    threshold: 0.50,
    resident_count: 0,
    camera_available: true,
  });

  const [sliderThreshold, setSliderThreshold] = useState(0.50);
  const [updatingThreshold, setUpdatingThreshold] = useState(false);
  const [reloadingDb, setReloadingDb] = useState(false);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    fetchGateStatus();
  }, []);

  const fetchGateStatus = async () => {
    try {
      const res = await gateApi.getStatus();
      setGateConfig(res.data);
      setSliderThreshold(res.data.threshold);
    } catch {
      setNotification({
        type: 'warning',
        message: 'Could not fetch live gate status. Ensure FastAPI backend is active.',
      });
    }
  };

  const handleThresholdSave = async () => {
    setUpdatingThreshold(true);
    try {
      const res = await gateApi.updateThreshold(sliderThreshold);
      setGateConfig((prev) => ({ ...prev, threshold: res.data.threshold }));
      setNotification({ type: 'success', message: res.data.message });
    } catch {
      setNotification({ type: 'error', message: 'Failed to update threshold.' });
    } finally {
      setUpdatingThreshold(false);
    }
  };

  const handleReloadDb = async () => {
    setReloadingDb(true);
    try {
      const res = await gateApi.reloadDatabase();
      setGateConfig((prev) => ({ ...prev, resident_count: res.data.resident_count }));
      setNotification({ type: 'success', message: res.data.message });
    } catch {
      setNotification({ type: 'error', message: 'Failed to reload resident database.' });
    } finally {
      setReloadingDb(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-navy-800">
        <div>
          <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2">
            <Video className="w-6 h-6 text-cyan-400" />
            <span>Live Security Gate Monitor</span>
          </h2>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Real-time optical access control with facial verification & instant threshold adaptation
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Badge variant="cyan" size="sm">
            {gateConfig.resident_count} Enrolled Residents
          </Badge>
          <button
            onClick={handleReloadDb}
            disabled={reloadingDb}
            className="inline-flex items-center space-x-2 px-3 py-2 rounded-xl bg-navy-900 hover:bg-navy-800 border border-navy-700 text-xs font-semibold text-slate-300 transition-colors disabled:opacity-50"
            title="Reload SQLite resident cache"
          >
            <RefreshCw size={14} className={reloadingDb ? 'animate-spin' : ''} />
            <span>Reload DB</span>
          </button>
        </div>
      </div>

      {notification && (
        <Alert
          type={notification.type}
          message={notification.message}
          onClose={() => setNotification(null)}
        />
      )}

      {/* Main Viewport Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Video Viewport (2 cols) */}
        <div className="lg:col-span-2 rounded-2xl bg-navy-900/90 border border-navy-800 overflow-hidden shadow-2xl flex flex-col">
          {/* Top Video Header */}
          <div className="p-4 bg-navy-950/80 border-b border-navy-800 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Gate Camera 01 — Frontal Portal
              </span>
            </div>
            <div className="flex items-center space-x-2 font-mono text-[11px] text-slate-400">
              <span>Threshold: {gateConfig.threshold.toFixed(2)}</span>
            </div>
          </div>

          {/* Viewport Display Area */}
          <div className="relative aspect-video bg-navy-950 flex items-center justify-center p-6 text-center">
            {/* Overlay Grid lines */}
            <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-40 pointer-events-none" />

            {/* Target Reticle in Center */}
            <div className="relative z-10 max-w-md p-6 rounded-2xl bg-navy-900/80 border border-navy-700/80 backdrop-blur-md shadow-2xl">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600/30 to-cyan-500/20 border border-cyan-500/30 flex items-center justify-center mx-auto mb-4 text-cyan-400">
                <Camera size={32} />
              </div>

              <h4 className="text-base font-bold text-white">
                Live Gate Stream Interface
              </h4>
              <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                OpenCV captures and matches entrant faces against all 22 registered SQLite encodings.
              </p>

              <div className="mt-5 p-3 rounded-xl bg-navy-950 border border-navy-800 text-left text-xs space-y-1.5 font-mono">
                <div className="flex justify-between text-slate-400">
                  <span>OpenCV Window Mode:</span>
                  <span className="text-emerald-400 font-bold">Supported via CLI</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>FastAPI Stream (Phase 5):</span>
                  <span className="text-cyan-400">Ready for MJPEG stream</span>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Feed Status Strip */}
          <div className="p-3 bg-navy-950/90 border-t border-navy-800 flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center space-x-2">
              <ShieldCheck size={14} className="text-emerald-400" />
              <span>Gate Decision: <strong className="text-white">Standby (Awaiting Entrant)</strong></span>
            </span>
            <span className="font-mono text-[11px]">FPS: Standby</span>
          </div>
        </div>

        {/* Right: Controls & Parameters (1 col) */}
        <div className="space-y-6">
          {/* Threshold Tuning Box */}
          <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-navy-800">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <Sliders className="w-4 h-4 text-blue-400" />
                <span>Recognition Threshold</span>
              </h3>
              <Badge variant="cyan" size="xs">
                {sliderThreshold.toFixed(2)}
              </Badge>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-xs text-slate-400">
                <span>0.10 (Strict)</span>
                <span>0.50 (Default)</span>
                <span>0.95 (Lenient)</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.95"
                step="0.05"
                value={sliderThreshold}
                onChange={(e) => setSliderThreshold(parseFloat(e.target.value))}
                className="w-full h-2 bg-navy-950 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Euclidean cutoff: faces with distance below this threshold are classified as <strong className="text-emerald-400">ENTRY ALLOWED</strong>; above are <strong className="text-rose-400">ENTRY REJECTED</strong>.
              </p>
            </div>

            <button
              onClick={handleThresholdSave}
              disabled={updatingThreshold}
              className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20 transition-all disabled:opacity-50"
            >
              {updatingThreshold ? 'Updating Threshold...' : 'Apply Threshold'}
            </button>
          </div>

          {/* Quick Guidance Box */}
          <div className="p-5 rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
              <Activity size={14} className="text-cyan-400" />
              <span>Keyboard Shortcuts (CLI Mode)</span>
            </h4>
            <ul className="text-xs text-slate-300 space-y-1.5 font-mono">
              <li className="flex justify-between p-1.5 rounded bg-navy-950/60">
                <span className="text-slate-400">Q / ESC</span>
                <span className="text-white">Exit Gate Feed</span>
              </li>
              <li className="flex justify-between p-1.5 rounded bg-navy-950/60">
                <span className="text-slate-400">+ / -</span>
                <span className="text-white">Adjust Threshold</span>
              </li>
              <li className="flex justify-between p-1.5 rounded bg-navy-950/60">
                <span className="text-slate-400">R</span>
                <span className="text-white">Hot Reload DB</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
