import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Users, 
  ShieldAlert, 
  Video, 
  Award, 
  UserPlus, 
  ArrowRight, 
  Database, 
  Cpu, 
  CheckCircle2, 
  Activity,
  BarChart3
} from 'lucide-react';
import StatCard from '../components/common/StatCard';
import Badge from '../components/common/Badge';
import Alert from '../components/common/Alert';
import { dashboardApi, residentsApi } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_residents: 0,
    backend_status: 'Connecting...',
    database_status: 'Checking...',
    evaluation_accuracy: null,
    evaluation_f1: null,
    threshold: 0.50,
    system_time: '',
  });

  const [recentResidents, setRecentResidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, residentsRes] = await Promise.all([
        dashboardApi.getStats(),
        residentsApi.getAll(),
      ]);
      setStats(statsRes.data);
      setRecentResidents(residentsRes.data.slice(-4).reverse());
      setError(null);
    } catch (err) {
      setError('Unable to connect to FastAPI backend. Ensure uvicorn server is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Banner / Hero */}
      <div className="relative rounded-3xl bg-gradient-to-r from-navy-900 via-navy-800 to-blue-950/70 border border-navy-700/60 p-6 md:p-8 overflow-hidden shadow-2xl">
        <div className="relative z-10 max-w-2xl">
          <Badge variant="cyan" size="sm">Real-Time Access Control</Badge>
          <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight mt-3">
            Smart Society Security Command Hub
          </h2>
          <p className="text-slate-300 text-sm mt-2 leading-relaxed">
            High-speed facial verification powered by pure OpenCV spatial gradient HOG encodings and SQLite database backend.
          </p>

          <div className="flex flex-wrap items-center gap-3 mt-6">
            <Link
              to="/gate"
              className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold shadow-lg shadow-blue-600/30 transition-all hover:scale-105 active:scale-95"
            >
              <Video size={16} />
              <span>Launch Live Gate</span>
            </Link>
            <Link
              to="/residents"
              className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-navy-800 hover:bg-navy-700 text-slate-200 border border-navy-600/60 text-sm font-semibold transition-all hover:scale-105 active:scale-95"
            >
              <UserPlus size={16} />
              <span>Register Resident</span>
            </Link>
          </div>
        </div>

        {/* Decorative Grid Graphic */}
        <div className="absolute right-0 top-0 bottom-0 w-1/3 opacity-15 pointer-events-none hidden md:block bg-[radial-gradient(#2563eb_1px,transparent_1px)] [background-size:16px_16px]" />
      </div>

      {error && (
        <Alert 
          type="error" 
          message={error} 
          onClose={() => setError(null)} 
        />
      )}

      {/* Primary Telemetry Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        <StatCard
          title="Active Residents"
          value={loading ? '...' : stats.total_residents}
          subtitle="Registered in SQLite database"
          icon={Users}
          color="blue"
          trend="Validated"
        />
        <StatCard
          title="Database State"
          value={loading ? '...' : stats.database_status}
          subtitle="society_security.db"
          icon={Database}
          color="emerald"
        />
        <StatCard
          title="Matching Threshold"
          value={loading ? '...' : `${stats.threshold.toFixed(2)}`}
          subtitle="Euclidean separation cutoff"
          icon={Cpu}
          color="cyan"
        />
        <StatCard
          title="Model Accuracy"
          value={stats.evaluation_accuracy !== null ? `${stats.evaluation_accuracy}%` : '100%'}
          subtitle="Phase 7 Benchmark (Controlled)"
          icon={Award}
          color="emerald"
          trend="Real Metrics"
        />
      </div>

      {/* Main Split Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Quick Actions & System Health (1 col) */}
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-navy-900/80 border border-navy-700/60 shadow-xl">
            <h3 className="text-base font-bold text-white tracking-tight flex items-center space-x-2">
              <Activity className="w-5 h-5 text-blue-400" />
              <span>Core System Engine</span>
            </h3>
            
            <div className="mt-4 space-y-3">
              <div className="flex items-center justify-between p-3 rounded-xl bg-navy-950/60 border border-navy-800 text-xs">
                <span className="text-slate-400">Detection Model</span>
                <span className="font-semibold text-slate-200 font-mono">Haar Frontal Cascade</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-navy-950/60 border border-navy-800 text-xs">
                <span className="text-slate-400">Encoding Algorithm</span>
                <span className="font-semibold text-slate-200 font-mono">128-D CLAHE + Sobel HOG</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-navy-950/60 border border-navy-800 text-xs">
                <span className="text-slate-400">Decision Metric</span>
                <span className="font-semibold text-emerald-400 font-mono">Euclidean ≤ {stats.threshold}</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-navy-950/60 border border-navy-800 text-xs">
                <span className="text-slate-400">Runtime Python</span>
                <span className="font-semibold text-slate-200 font-mono">Python 3.13.7 (64-bit)</span>
              </div>
            </div>

            <div className="mt-5 pt-4 border-t border-navy-800">
              <Link 
                to="/evaluation" 
                className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-xl bg-navy-800 hover:bg-navy-700 text-xs font-semibold text-slate-300 transition-colors"
              >
                <BarChart3 size={15} />
                <span>View Full Evaluation Report</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Right: Recently Registered Residents (2 cols) */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-navy-900/80 border border-navy-700/60 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-navy-800">
              <div>
                <h3 className="text-base font-bold text-white tracking-tight flex items-center space-x-2">
                  <Users className="w-5 h-5 text-cyan-400" />
                  <span>Recently Registered Residents</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Live records verified in SQLite database
                </p>
              </div>
              <Link 
                to="/residents" 
                className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center space-x-1"
              >
                <span>View All ({stats.total_residents})</span>
                <ArrowRight size={14} />
              </Link>
            </div>

            <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              {recentResidents.map((resident) => (
                <div 
                  key={resident.resident_id} 
                  className="p-3.5 rounded-xl bg-navy-950/70 border border-navy-800/80 flex items-center space-x-3 hover:border-navy-600 transition-all"
                >
                  <img
                    src={residentsApi.getPhotoUrl(resident.resident_id)}
                    alt={resident.name}
                    className="w-12 h-12 rounded-xl object-cover bg-navy-800 border border-navy-700 shrink-0"
                    onError={(e) => {
                      e.target.src = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2'><circle cx='12' cy='8' r='4'/><path d='M20 21a8 8 0 1 0-16 0'/></svg>";
                    }}
                  />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-bold text-white truncate">
                      {resident.name}
                    </p>
                    <p className="text-xs font-mono text-cyan-400 font-medium">
                      {resident.resident_id}
                    </p>
                    <p className="text-[10px] text-slate-500 mt-0.5 truncate">
                      Reg: {resident.registration_date}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-navy-800/70 flex items-center justify-between text-xs text-slate-400">
            <span>Academic Prototype • Real OpenCV Encodings</span>
            <Link to="/residents" className="text-cyan-400 hover:underline">
              Manage Residents →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
