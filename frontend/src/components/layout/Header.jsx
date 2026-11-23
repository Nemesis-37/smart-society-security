import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { ShieldCheck, Clock, Activity, Menu, ShieldAlert } from 'lucide-react';
import { healthApi } from '../../services/api';

const routeTitles = {
  '/': { title: 'SURVEILLANCE COMMAND HUB', subtitle: 'REAL-TIME ACCESS CONTROL & SYSTEM METRICS' },
  '/residents': { title: 'RESIDENT ROSTER & ENROLLMENT', subtitle: 'AUTHENTICATED PERSONNEL DIRECTORY & HOG ENCODINGS' },
  '/gate': { title: 'LIVE SURVEILLANCE GATE MONITOR', subtitle: 'OPTICAL FACIAL VERIFICATION & DECISION ENGINE' },
  '/logs': { title: 'ACCESS AUDIT & EVENT LOGS', subtitle: 'TAMPER-RESISTANT SQLite VERIFICATION AUDIT TRAIL' },
  '/evaluation': { title: 'MODEL EVALUATION & BENCHMARKS', subtitle: 'PHASE 7 EMPIRICAL PERFORMANCE & ROBUSTNESS DATA' },
  '/settings': { title: 'HARDWARE & SYSTEM CONFIGURATION', subtitle: 'ALGORITHM HYPERPARAMETERS & DEVICE BINDINGS' },
};

export default function Header({ collapsed, onMobileMenuToggle }) {
  const location = useLocation();
  const current = routeTitles[location.pathname] || {
    title: 'SENTINEL SECURITY SYSTEM',
    subtitle: 'TACTICAL ACCESS CONTROL',
  };

  const [time, setTime] = useState(new Date().toLocaleTimeString());
  const [online, setOnline] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await healthApi.getHealth();
        setOnline(res.data.status === 'healthy');
      } catch {
        setOnline(false);
      }
    };
    check();
    const interval = setInterval(check, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-20 h-16 bg-graphite-950/90 backdrop-blur-md border-b border-graphite-800 px-4 md:px-8 flex items-center justify-between">
      {/* Left Title & Mobile Hamburger */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onMobileMenuToggle}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-graphite-850 md:hidden"
        >
          <Menu size={20} />
        </button>
        <div>
          <h1 className="text-sm md:text-base font-extrabold text-white tracking-wider font-mono flex items-center space-x-2">
            <span className="w-1.5 h-3.5 bg-crimson-600 inline-block rounded-xs" />
            <span>{current.title}</span>
          </h1>
          <p className="text-[10px] text-slate-400 font-mono tracking-widest uppercase hidden sm:block">
            {current.subtitle}
          </p>
        </div>
      </div>

      {/* Right Telemetry */}
      <div className="flex items-center space-x-3">
        {/* Tactical Live Clock */}
        <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-graphite-900 border border-graphite-800 text-xs text-slate-200 font-mono">
          <Clock size={13} className="text-amber-400" />
          <span className="tracking-widest">{time}</span>
        </div>

        {/* System Health Status Indicator */}
        <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg border text-xs font-mono font-bold tracking-wider ${
          online 
            ? 'bg-status-allowed/10 border-status-allowed/30 text-status-allowed' 
            : 'bg-crimson-600/10 border-crimson-600/30 text-crimson-500'
        }`}>
          <span className={`w-2 h-2 rounded-full ${online ? 'bg-status-allowed animate-pulse' : 'bg-crimson-600'}`} />
          <span className="text-[10px] uppercase">
            {online ? 'GATE ONLINE' : 'DISCONNECTED'}
          </span>
        </div>
      </div>
    </header>
  );
}
