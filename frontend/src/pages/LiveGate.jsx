import React, { useState, useEffect, useRef } from 'react';
import { 
  Video, 
  VideoOff, 
  ShieldCheck, 
  ShieldAlert, 
  Sliders, 
  RefreshCw, 
  Camera, 
  AlertTriangle,
  Play,
  Square,
  Activity,
  UserCheck,
  UserX,
  Gauge,
  Info,
  Radio
} from 'lucide-react';
import Badge from '../components/common/Badge';
import Alert from '../components/common/Alert';
import { gateApi } from '../services/api';

export default function LiveGate() {
  const [gateConfig, setGateConfig] = useState({
    camera_active: false,
    gate_status: 'GATE IDLE',
    fps: 0,
    threshold: 0.50,
    resident_count: 0,
    last_decision: {
      decision: 'NO FACE',
      resident_id: null,
      name: 'No face detected',
      distance: null,
      confidence: 0,
      timestamp: null,
    },
    faces_detected: 0,
  });

  const [sliderThreshold, setSliderThreshold] = useState(0.50);
  const [streaming, setStreaming] = useState(false);
  const [loadingCamera, setLoadingCamera] = useState(false);
  const [updatingThreshold, setUpdatingThreshold] = useState(false);
  const [reloadingDb, setReloadingDb] = useState(false);
  const [streamError, setStreamError] = useState(false);
  const [notification, setNotification] = useState(null);
  
  const streamKeyRef = useRef(Date.now());

  useEffect(() => {
    fetchGateStatus();
    const interval = setInterval(fetchGateStatus, 1500);
    return () => clearInterval(interval);
  }, []);

  const fetchGateStatus = async () => {
    try {
      const res = await gateApi.getStatus();
      setGateConfig(res.data);
      if (res.data.camera_active && !streaming) {
        setStreaming(true);
      }
    } catch {
      // silent catch for background polling
    }
  };

  const handleStartCamera = async () => {
    setLoadingCamera(true);
    setStreamError(false);
    try {
      const res = await gateApi.start();
      if (res.data.success || res.data.camera_active) {
        setStreaming(true);
        streamKeyRef.current = Date.now();
        setNotification({ type: 'success', message: res.data.message });
        fetchGateStatus();
      } else {
        setNotification({ 
          type: 'error', 
          message: res.data.message || 'Camera hardware could not be initialized. Verify webcam device connection.' 
        });
      }
    } catch (err) {
      setNotification({
        type: 'error',
        message: 'Failed to communicate with camera service. Ensure FastAPI backend is running.',
      });
    } finally {
      setLoadingCamera(false);
    }
  };

  const handleStopCamera = async () => {
    setLoadingCamera(true);
    try {
      const res = await gateApi.stop();
      setStreaming(false);
      setNotification({ type: 'info', message: res.data.message });
      fetchGateStatus();
    } catch (err) {
      setNotification({ type: 'error', message: 'Failed to stop camera.' });
    } finally {
      setLoadingCamera(false);
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

  const decision = gateConfig.last_decision;
  const isAllowed = decision?.decision === 'ENTRY ALLOWED';
  const isRejected = decision?.decision === 'ENTRY REJECTED';

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-graphite-800">
        <div>
          <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2 font-mono">
            <Video className="w-6 h-6 text-crimson-500" />
            <span>LIVE SURVEILLANCE GATE</span>
          </h2>
          <p className="text-xs md:text-sm text-slate-400 mt-1 font-mono">
            Real-time optical access control with facial verification & instant threshold adaptation
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Badge variant={gateConfig.camera_active ? 'allowed' : 'neutral'} size="sm">
            {gateConfig.camera_active ? 'CAMERA ACTIVE' : 'CAMERA STANDBY'}
          </Badge>
          <Badge variant="crimson" size="sm">
            {gateConfig.resident_count} PROFILES CACHED
          </Badge>
          <button
            onClick={handleReloadDb}
            disabled={reloadingDb}
            className="inline-flex items-center space-x-2 px-3 py-2 rounded-xl bg-graphite-900 hover:bg-graphite-800 border border-graphite-700 text-xs font-mono uppercase tracking-wider text-slate-300 transition-colors disabled:opacity-50"
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

      {/* Main Viewport & Real-time Telemetry Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Video Viewport (2 cols) */}
        <div className="lg:col-span-2 rounded-2xl bg-graphite-900 border border-graphite-800 overflow-hidden shadow-2xl flex flex-col">
          {/* Top Video Header */}
          <div className="p-4 bg-graphite-950 border-b border-graphite-800 flex items-center justify-between font-mono text-xs">
            <div className="flex items-center space-x-2">
              <span className={`w-2.5 h-2.5 rounded-full ${gateConfig.camera_active ? 'bg-status-allowed animate-pulse' : 'bg-slate-500'}`} />
              <span className="font-bold text-white uppercase tracking-wider">
                FEED: CAM-01 [PRIMARY PORTAL]
              </span>
            </div>
            
            <div className="flex items-center space-x-4 text-[11px] text-slate-400">
              <span>FPS: {gateConfig.fps || '0.0'}</span>
              <span>CUTOFF: {gateConfig.threshold.toFixed(2)}</span>
            </div>
          </div>

          {/* Viewport Display Area */}
          <div className="relative aspect-video bg-black flex items-center justify-center overflow-hidden">
            {streaming && !streamError ? (
              <img
                src={`${gateApi.getStreamUrl()}?t=${streamKeyRef.current}`}
                alt="Live Gate Stream"
                className="w-full h-full object-contain"
                onError={() => {
                  setStreamError(true);
                  setStreaming(false);
                }}
              />
            ) : (
              <div className="p-8 text-center max-w-md">
                <div className="w-16 h-16 rounded-2xl bg-graphite-900 border border-graphite-800 flex items-center justify-center mx-auto mb-4 text-slate-400 shadow-xl">
                  {streamError ? <AlertTriangle size={32} className="text-amber-400" /> : <Camera size={32} />}
                </div>

                <h4 className="text-base font-bold text-white font-mono">
                  {streamError ? 'CAMERA FEED INTERRUPTED' : 'SURVEILLANCE FEED STANDBY'}
                </h4>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  {streamError
                    ? 'The video stream could not be acquired. Check camera permissions or ensure another program is not holding the webcam.'
                    : 'Click "Activate Camera Feed" below to initiate the OpenCV webcam capture session and facial recognition pipeline.'}
                </p>

                <div className="mt-5">
                  <button
                    onClick={handleStartCamera}
                    disabled={loadingCamera}
                    className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-crimson-600 hover:bg-crimson-500 text-white text-xs font-bold font-mono uppercase tracking-wider shadow-lg shadow-crimson-600/30 transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                  >
                    {loadingCamera ? <RefreshCw size={14} className="animate-spin" /> : <Play size={14} />}
                    <span>Activate Camera Feed</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Bottom Feed Status & Controls Strip */}
          <div className="p-4 bg-graphite-950 border-t border-graphite-800 flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
            {/* Live Camera Controls */}
            <div className="flex items-center space-x-2">
              {!streaming ? (
                <button
                  onClick={handleStartCamera}
                  disabled={loadingCamera}
                  className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-status-allowed hover:bg-emerald-600 text-white font-bold transition-all disabled:opacity-50"
                >
                  <Play size={13} />
                  <span>Start Camera</span>
                </button>
              ) : (
                <button
                  onClick={handleStopCamera}
                  disabled={loadingCamera}
                  className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-crimson-600 hover:bg-crimson-500 text-white font-bold transition-all disabled:opacity-50"
                >
                  <Square size={13} />
                  <span>Stop Camera</span>
                </button>
              )}
            </div>

            {/* Current Decision Pill */}
            <div className="flex items-center space-x-2">
              <span className="text-slate-400">STATE:</span>
              <span className={`px-2.5 py-1 rounded-md font-bold font-mono text-xs ${
                isAllowed 
                  ? 'bg-status-allowed/15 text-status-allowed border border-status-allowed/30' 
                  : isRejected 
                  ? 'bg-status-rejected/15 text-status-rejected border border-status-rejected/30' 
                  : 'bg-graphite-800 text-slate-300 border border-graphite-700'
              }`}>
                {gateConfig.gate_status}
              </span>
            </div>
          </div>
        </div>

        {/* Right: Decision Panel & Controls (1 col) */}
        <div className="space-y-6">
          {/* Live Decision Card */}
          <div className={`p-6 rounded-2xl bg-graphite-900 border shadow-xl transition-all ${
            isAllowed 
              ? 'border-status-allowed/40 tactical-glow-allowed' 
              : isRejected 
              ? 'border-status-rejected/40 tactical-glow-crimson' 
              : 'border-graphite-800'
          }`}>
            <div className="flex items-center justify-between pb-3 border-b border-graphite-800">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5 font-mono">
                <Activity size={14} className="text-crimson-500" />
                <span>Verification Decision</span>
              </h3>
              <Badge variant={isAllowed ? 'allowed' : isRejected ? 'rejected' : 'neutral'} size="xs">
                {decision?.decision || 'STANDBY'}
              </Badge>
            </div>

            <div className="mt-4 space-y-3">
              {/* Entrant Name */}
              <div className="flex items-center space-x-3 p-3 rounded-xl bg-graphite-950 border border-graphite-800">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                  isAllowed 
                    ? 'bg-status-allowed/15 text-status-allowed' 
                    : isRejected 
                    ? 'bg-status-rejected/15 text-status-rejected' 
                    : 'bg-graphite-800 text-slate-400'
                }`}>
                  {isAllowed ? <UserCheck size={20} /> : <UserX size={20} />}
                </div>
                <div className="min-w-0 flex-1">
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold block font-mono">
                    Entrant Identity
                  </span>
                  <p className="text-sm font-bold text-white truncate">
                    {decision?.name || 'Awaiting face detection'}
                  </p>
                  {decision?.resident_id && (
                    <span className="text-xs font-mono text-crimson-400 font-bold">
                      ID: {decision.resident_id}
                    </span>
                  )}
                </div>
              </div>

              {/* Distance & Confidence Telemetry */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2.5 rounded-xl bg-graphite-950 border border-graphite-800">
                  <span className="text-[10px] uppercase text-slate-400 block font-semibold">Face Distance</span>
                  <span className="text-white font-bold">
                    {decision?.distance !== null && decision?.distance !== undefined 
                      ? `${decision.distance.toFixed(4)}` 
                      : 'N/A'}
                  </span>
                </div>
                <div className="p-2.5 rounded-xl bg-graphite-950 border border-graphite-800">
                  <span className="text-[10px] uppercase text-slate-400 block font-semibold">Match Confidence</span>
                  <span className={`font-bold ${isAllowed ? 'text-status-allowed' : 'text-slate-400'}`}>
                    {decision?.confidence ? `${(decision.confidence * 100).toFixed(1)}%` : '0.0%'}
                  </span>
                </div>
              </div>

              {/* Detection Multiplicity */}
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-graphite-950 border border-graphite-800 text-xs font-mono">
                <span className="text-slate-400">Faces in Viewport:</span>
                <span className="text-white font-bold">{gateConfig.faces_detected}</span>
              </div>
            </div>
          </div>

          {/* Threshold Tuning Box */}
          <div className="p-6 rounded-2xl bg-graphite-900 border border-graphite-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-graphite-800">
              <h3 className="text-xs font-bold uppercase tracking-wider text-white flex items-center space-x-1.5 font-mono">
                <Sliders className="w-4 h-4 text-crimson-500" />
                <span>Threshold Tuning</span>
              </h3>
              <span className="text-xs font-mono font-bold text-crimson-400">
                {sliderThreshold.toFixed(2)}
              </span>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-[11px] text-slate-400 font-mono">
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
                className="w-full h-2 bg-graphite-950 rounded-lg appearance-none cursor-pointer accent-crimson-600"
              />
            </div>

            <button
              onClick={handleThresholdSave}
              disabled={updatingThreshold}
              className="w-full py-2 rounded-xl bg-crimson-600 hover:bg-crimson-500 text-white text-xs font-bold font-mono uppercase tracking-wider shadow-md shadow-crimson-600/20 transition-all disabled:opacity-50"
            >
              {updatingThreshold ? 'Updating...' : 'Save New Cutoff'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
