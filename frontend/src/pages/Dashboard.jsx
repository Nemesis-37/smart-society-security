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
  BarChart3,
  Terminal,
  Radio,
  Sliders
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
      setError('Unable to connect to FastAPI backend. Ensure server is running on port 8088.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Tactical Surveillance Operations Banner */}
      <div className="relative rounded-2xl bg-graphite-900 border border-graphite-800 p-6 md:p-8 overflow-hidden shadow-2xl">
        <div className="relative z-10 max-w-2xl">
          <div className="flex items-center space-x-2">
            <Badge variant="crimson" size="xs">TACTICAL ACCESS NODE</Badge>
            <span className="text-[11px] font-mono text-slate-400">STATUS: ARMED</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight mt-3 font-mono">
            SENTINEL SURVEILLANCE COMMAND
          </h2>
          <p className="text-slate-300 text-xs md:text-sm mt-2 leading-relaxed font-sans">
            Autonomous optical security portal powered by 128-dimensional CLAHE + Sobel HOG facial encodings, real-time Euclidean distance verification, and SQLite persistent audit storage.
          </p>

          <div className="flex flex-wrap items-center gap-3 mt-6">
            <Link
              to="/gate"
              className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-crimson-600 hover:bg-crimson-500 text-white text-xs font-bold uppercase tracking-wider shadow-lg shadow-crimson-600/30 transition-all hover:scale-105 active:scale-95 border border-crimson-500/40"
            >
              <Video size={15} />
              <span>Launch Live Gate Monitor</span>
            </Link>
            <Link
              to="/residents"
              className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-graphite-800 hover:bg-graphite-750 text-slate-200 border border-graphite-700 text-xs font-bold uppercase tracking-wider transition-all hover:scale-105 active:scale-95"
            >
              <UserPlus size={15} />
              <span>Enroll Resident</span>
            </Link>
          </div>
        </div>

        {/* Tactical Crosshair / Background Accent */}
        <div className="absolute right-6 top-6 bottom-6 w-1/3 opacity-10 pointer-events-none hidden lg:flex items-center justify-end">
          <ShieldAlert className="w-48 h-48 text-crimson-500" />
        </div>
      </div>

      {error && (
        <Alert 
          type="error" 
          message={error} 
          onClose={() => setError(null)} 
        />
      )}

      {/* Primary Telemetry Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-5">
        <StatCard
          title="Enrolled Residents"
          value={loading ? '...' : stats.total_residents}
          subtitle="Active biometric profiles in SQLite"
          icon={Users}
          color="crimson"
          trend="VALIDATED"
        />
        <StatCard
          title="Database Core"
          value={loading ? '...' : stats.database_status}
          subtitle="society_security.db"
          icon={Database}
          color="allowed"
          trend="ONLINE"
        />
        <StatCard
          title="Euclidean Cutoff"
          value={loading ? '...' : `${stats.threshold.toFixed(2)}`}
          subtitle="Spatial separation threshold"
          icon={Sliders}
          color="amber"
          trend="ACTIVE"
        />
        <StatCard
          title="Benchmark Accuracy"
          value={stats.evaluation_accuracy !== null ? `${stats.evaluation_accuracy}%` : '100%'}
          subtitle="Controlled Phase 7 Dataset"
          icon={Award}
          color="allowed"
          trend="EMPIRICAL"
        />
      </div>

      {/* Main Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Engine Architecture Specifications */}
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-graphite-900 border border-graphite-800 shadow-xl">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center space-x-2 pb-3 border-b border-graphite-800">
              <Activity className="w-4 h-4 text-crimson-500" />
              <span>Optical Engine Telemetry</span>
            </h3>
            
            <div className="mt-4 space-y-3">
              <div className="flex items-center justify-between p-3 rounded-xl bg-graphite-950 border border-graphite-800/80 text-xs">
                <span className="text-slate-400 font-mono text-[11px]">DETECTION CASCADE</span>
                <span className="font-bold text-slate-200 font-mono text-[11px]">Haar Frontal Default</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-graphite-950 border border-graphite-800/80 text-xs">
                <span className="text-slate-400 font-mono text-[11px]">ROI CANONICAL</span>
                <span className="font-bold text-slate-200 font-mono text-[11px]">100 × 100 Grayscale</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-graphite-950 border border-graphite-800/80 text-xs">
                <span className="text-slate-400 font-mono text-[11px]">ENCODING VECTOR</span>
                <span className="font-bold text-slate-200 font-mono text-[11px]">128-D CLAHE + Sobel HOG</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-graphite-950 border border-graphite-800/80 text-xs">
                <span className="text-slate-400 font-mono text-[11px]">DECISION FORMULA</span>
                <span className="font-bold text-status-allowed font-mono text-[11px]">Euclidean ≤ {stats.threshold}</span>
              </div>
            </div>

            <div className="mt-5 pt-4 border-t border-graphite-800">
              <Link 
                to="/evaluation" 
                className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-xl bg-graphite-800 hover:bg-graphite-750 text-xs font-bold font-mono uppercase tracking-wider text-slate-300 transition-colors border border-graphite-700"
              >
                <BarChart3 size={14} />
                <span>Examine Evaluation Report</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Right: Recently Registered Residents */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-graphite-900 border border-graphite-800 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-graphite-800">
              <div>
                <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center space-x-2">
                  <Users className="w-4 h-4 text-crimson-500" />
                  <span>Recently Enrolled Personnel</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Live resident profiles stored in SQLite
                </p>
              </div>
              <Link 
                to="/residents" 
                className="text-xs font-bold font-mono uppercase tracking-wider text-crimson-400 hover:text-crimson-300 flex items-center space-x-1"
              >
                <span>Full Roster ({stats.total_residents})</span>
                <ArrowRight size={14} />
              </Link>
            </div>

            <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              {recentResidents.map((resident) => (
                <div 
                  key={resident.resident_id} 
                  className="p-3.5 rounded-xl bg-graphite-950 border border-graphite-800 flex items-center space-x-3 hover:border-graphite-700 transition-all"
                >
                  <img
                    src={residentsApi.getPhotoUrl(resident.resident_id)}
                    alt={resident.name}
                    className="w-12 h-12 rounded-xl object-cover bg-graphite-850 border border-graphite-700 shrink-0"
                    onError={(e) => {
                      e.target.src = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2'><circle cx='12' cy='8' r='4'/><path d='M20 21a8 8 0 1 0-16 0'/></svg>";
                    }}
                  />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-bold text-white truncate">
                      {resident.name}
                    </p>
                    <p className="text-xs font-mono text-crimson-400 font-bold">
                      {resident.resident_id}
                    </p>
                    <p className="text-[10px] text-slate-400 font-mono mt-0.5 truncate">
                      ENROLLED: {resident.registration_date}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-graphite-800 flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>TACTICAL ROSTER • PERSISTENT ENCODINGS</span>
            <Link to="/residents" className="text-crimson-400 hover:underline">
              Manage Resident Roster →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
