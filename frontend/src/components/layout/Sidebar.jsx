import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  ShieldCheck, 
  LayoutDashboard, 
  Users, 
  Video, 
  FileText, 
  BarChart3, 
  Settings,
  ChevronLeft,
  ChevronRight,
  Server
} from 'lucide-react';

export default function Sidebar({ collapsed, setCollapsed }) {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Residents', path: '/residents', icon: Users },
    { name: 'Live Security Gate', path: '/gate', icon: Video },
    { name: 'Entry Logs', path: '/logs', icon: FileText },
    { name: 'Evaluation', path: '/evaluation', icon: BarChart3 },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside 
      className={`fixed top-0 left-0 z-30 h-screen transition-all duration-300 ease-in-out border-r border-navy-700/50 bg-navy-900/95 backdrop-blur-md flex flex-col justify-between ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div>
        <div className="flex items-center justify-between h-16 px-4 border-b border-navy-700/50">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20 shrink-0">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            {!collapsed && (
              <div className="flex flex-col min-w-0">
                <span className="text-sm font-bold tracking-tight text-white truncate">
                  SMART SOCIETY
                </span>
                <span className="text-[10px] uppercase tracking-wider text-cyan-400 font-semibold truncate">
                  Security System
                </span>
              </div>
            )}
          </div>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-navy-800 transition-colors hidden md:block"
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-3.5 py-3 rounded-xl text-sm font-medium transition-all duration-200 group relative ${
                    isActive
                      ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm shadow-blue-500/10'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800/60'
                  } ${collapsed ? 'justify-center' : 'space-x-3'}`
                }
              >
                <Icon className={`w-5 h-5 shrink-0 transition-colors ${collapsed ? '' : ''}`} />
                {!collapsed && <span className="truncate">{item.name}</span>}
                {collapsed && (
                  <div className="absolute left-full ml-3 px-2.5 py-1 bg-navy-800 border border-navy-700 text-xs text-white rounded-md whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 shadow-xl">
                    {item.name}
                  </div>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-navy-700/50">
        <div className={`flex items-center ${collapsed ? 'justify-center' : 'space-x-3 px-2 py-1.5'} text-xs text-slate-500`}>
          <Server className="w-4 h-4 text-emerald-400 shrink-0" />
          {!collapsed && (
            <div className="truncate">
              <p className="font-semibold text-slate-300">FastAPI & OpenCV</p>
              <p className="text-[10px] text-slate-500 font-mono">v1.0.0 • SQLite</p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
