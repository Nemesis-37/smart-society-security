import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { ShieldCheck, Clock, Activity, Menu } from 'lucide-react';
import { healthApi } from '../../services/api';

const routeTitles = {
  '/': 'Security Overview Dashboard',
  '/residents': 'Resident Directory & Management',
  '/gate': 'Live Security Gate Monitor',
  '/logs': 'Gate Entry & Access Logs',
  '/evaluation': 'Model Performance & Evaluation',
  '/settings': 'System Settings & Hardware',
};

export default function Header({ collapsed, onMobileMenuToggle }) {
  const location = useLocation();
  const title = routeTitles[location.pathname] || 'Smart Society Security';

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
    <header className="sticky top-0 z-20 h-16 bg-navy-950/80 backdrop-blur-md border-b border-navy-800/80 px-4 md:px-8 flex items-center justify-between">
      {/* Left Title & Mobile Hamburger */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onMobileMenuToggle}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-navy-800 md:hidden"
        >
          <Menu size={20} />
        </button>
        <div>
          <h1 className="text-base md:text-lg font-bold text-white tracking-tight flex items-center space-x-2">
            <span>{title}</span>
          </h1>
          <p className="text-[11px] text-slate-400 hidden sm:block">
            Smart Access Control • Real-Time OpenCV Facial Verification
          </p>
        </div>
      </div>

      {/* Right Telemetry */}
      <div className="flex items-center space-x-4">
        {/* Live Clock */}
        <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-navy-900 border border-navy-800 text-xs text-slate-300 font-mono">
          <Clock size={13} className="text-cyan-400" />
          <span>{time}</span>
        </div>

        {/* System Health Badge */}
        <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg border text-xs font-semibold ${
          online 
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
            : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
        }`}>
          <span className={`w-2 h-2 rounded-full ${online ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
          <span className="uppercase tracking-wider text-[10px]">
            {online ? 'System Active' : 'Offline'}
          </span>
        </div>
      </div>
    </header>
  );
}
