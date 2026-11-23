import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  ShieldAlert, 
  LayoutDashboard, 
  Users, 
  Video, 
  FileText, 
  BarChart3, 
  Settings,
  ChevronLeft,
  ChevronRight,
  Radio,
  Lock
} from 'lucide-react';

export default function Sidebar({ collapsed, setCollapsed }) {
  const navItems = [
    { name: 'Command Overview', path: '/', icon: LayoutDashboard },
    { name: 'Resident Roster', path: '/residents', icon: Users },
    { name: 'Live Surveillance Gate', path: '/gate', icon: Video },
    { name: 'Access Audit Logs', path: '/logs', icon: FileText },
    { name: 'Evaluation & Benchmarks', path: '/evaluation', icon: BarChart3 },
    { name: 'System Hardware', path: '/settings', icon: Settings },
  ];

  return (
    <aside 
      className={`fixed top-0 left-0 z-30 h-screen transition-all duration-300 ease-in-out border-r border-graphite-800 bg-graphite-900/98 backdrop-blur-md flex flex-col justify-between ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div>
        <div className="flex items-center justify-between h-16 px-4 border-b border-graphite-800">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-10 h-10 rounded-xl bg-crimson-600 flex items-center justify-center shadow-lg shadow-crimson-600/30 shrink-0 border border-crimson-500/40">
              <ShieldAlert className="w-5 h-5 text-white" />
            </div>
            {!collapsed && (
              <div className="flex flex-col min-w-0">
                <span className="text-sm font-extrabold tracking-wider text-white truncate font-mono">
                  SENTINEL
                </span>
                <span className="text-[10px] tracking-widest text-slate-400 font-semibold truncate uppercase">
                  Society Security
                </span>
              </div>
            )}
          </div>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-graphite-800 transition-colors hidden md:block"
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>

        {/* Tactical Status Tag */}
        {!collapsed && (
          <div className="px-4 py-2 bg-graphite-950/60 border-b border-graphite-800/70 flex items-center justify-between text-[11px] font-mono">
            <span className="text-slate-400 flex items-center space-x-1.5">
              <Radio className="w-3 h-3 text-status-allowed animate-pulse" />
              <span>NODE: SEC-01</span>
            </span>
            <span className="text-slate-400 uppercase tracking-wider font-semibold">
              ARMED
            </span>
          </div>
        )}

        {/* Navigation Items */}
        <nav className="p-3 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-3.5 py-3 rounded-xl text-xs font-semibold uppercase tracking-wider transition-all duration-200 group relative ${
                    isActive
                      ? 'bg-crimson-600 text-white shadow-md shadow-crimson-600/25 border border-crimson-500/50'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-graphite-800/80 border border-transparent'
                  } ${collapsed ? 'justify-center' : 'space-x-3'}`
                }
              >
                <Icon className="w-4 h-4 shrink-0 transition-transform group-hover:scale-105" />
                {!collapsed && <span className="truncate">{item.name}</span>}
                {collapsed && (
                  <div className="absolute left-full ml-3 px-3 py-1.5 bg-graphite-850 border border-graphite-700 text-xs font-medium text-white rounded-lg whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 shadow-2xl">
                    {item.name}
                  </div>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-graphite-800 bg-graphite-950/50">
        <div className={`flex items-center ${collapsed ? 'justify-center' : 'space-x-3 px-2 py-1.5'} text-xs text-slate-400`}>
          <Lock className="w-4 h-4 text-crimson-500 shrink-0" />
          {!collapsed && (
            <div className="truncate">
              <p className="font-bold text-slate-200 font-mono text-[11px] uppercase tracking-wider">
                FastAPI • OpenCV
              </p>
              <p className="text-[10px] text-slate-400 font-mono">SQLite • 128-D HOG</p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
