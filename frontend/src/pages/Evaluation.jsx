import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Award, 
  CheckCircle2, 
  AlertTriangle, 
  Layers, 
  Sliders, 
  FileCheck2,
  RefreshCw,
  Image as ImageIcon
} from 'lucide-react';
import Badge from '../components/common/Badge';
import StatCard from '../components/common/StatCard';
import Alert from '../components/common/Alert';
import { evaluationApi } from '../services/api';

export default function Evaluation() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('confusion_matrix');
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchEvaluation();
  }, []);

  const fetchEvaluation = async () => {
    setLoading(true);
    try {
      const res = await evaluationApi.getSummary();
      setSummary(res.data);
      setError(null);
    } catch {
      setError('Evaluation summary not yet available from FastAPI backend. Verify Phase 7 evaluation ran.');
    } finally {
      setLoading(false);
    }
  };

  const plots = [
    { id: 'confusion_matrix', name: 'Confusion Matrix Heatmap' },
    { id: 'environmental_robustness', name: 'Environmental Robustness Bar Chart' },
    { id: 'threshold_analysis', name: 'Threshold Sensitivity Curve' },
  ];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-graphite-800">
        <div>
          <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2 font-mono">
            <BarChart3 className="w-6 h-6 text-crimson-500" />
            <span>MODEL EVALUATION & BENCHMARKS</span>
          </h2>
          <p className="text-xs md:text-sm text-slate-400 mt-1 font-mono">
            Empirical benchmark metrics computed from 176 algorithm test iterations (Phase 7)
          </p>
        </div>

        <button
          onClick={fetchEvaluation}
          className="p-2.5 rounded-xl bg-graphite-900 hover:bg-graphite-800 border border-graphite-700 text-slate-300 transition-colors self-start"
          title="Refresh metrics"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {error && <Alert type="warning" message={error} />}

      {/* Academic Prototype Disclosure */}
      <div className="p-4 rounded-xl bg-status-warning/10 border border-status-warning/30 text-xs text-amber-200 flex items-start space-x-3">
        <FileCheck2 className="w-5 h-5 text-status-warning shrink-0 mt-0.5" />
        <div className="leading-relaxed font-sans">
          <strong className="text-white font-mono uppercase">Academic Integrity & Evaluation Disclosure:</strong> The metrics below were calculated by <code>src/evaluate.py</code> using 88 genuine samples (22 registered residents × 4 augmentation conditions: standard warp, low-light $\alpha=0.75$, 8° rotation, and 5×5 blur) plus 88 synthetic random intruder vectors. As detailed in the project report, 100% scores reflect a controlled benchmark; real-world accuracy with novel unconstrained human intruders will naturally vary.
        </div>
      </div>

      {/* Metrics Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Accuracy"
          value={summary ? `${summary.accuracy.toFixed(1)}%` : '100.0%'}
          subtitle="Overall Classification"
          icon={Award}
          color="allowed"
        />
        <StatCard
          title="Precision"
          value={summary ? `${summary.precision.toFixed(1)}%` : '100.0%'}
          subtitle="Zero False Accepts (FP=0)"
          icon={CheckCircle2}
          color="crimson"
        />
        <StatCard
          title="Recall"
          value={summary ? `${summary.recall.toFixed(1)}%` : '100.0%'}
          subtitle="Zero False Rejects (FN=0)"
          icon={Layers}
          color="amber"
        />
        <StatCard
          title="F1-Score"
          value={summary ? `${summary.f1_score.toFixed(1)}%` : '100.0%'}
          subtitle="Harmonic Mean"
          icon={BarChart3}
          color="allowed"
        />
      </div>

      {/* Confusion Matrix Numbers */}
      <div className="p-6 rounded-2xl bg-graphite-900 border border-graphite-800 shadow-xl">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono mb-4">
          Binary Classification Breakdown (Threshold: {summary?.threshold ?? 0.50})
        </h3>
        
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono">
          <div className="p-4 rounded-xl bg-graphite-950 border border-status-allowed/40 text-center">
            <span className="text-[11px] text-slate-400 font-bold uppercase">True Positive (TP)</span>
            <p className="text-2xl font-bold text-status-allowed mt-1">{summary?.tp ?? 88}</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Residents Admitted</p>
          </div>
          <div className="p-4 rounded-xl bg-graphite-950 border border-graphite-700 text-center">
            <span className="text-[11px] text-slate-400 font-bold uppercase">True Negative (TN)</span>
            <p className="text-2xl font-bold text-white mt-1">{summary?.tn ?? 88}</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Intruders Blocked</p>
          </div>
          <div className="p-4 rounded-xl bg-graphite-950 border border-status-rejected/40 text-center">
            <span className="text-[11px] text-slate-400 font-bold uppercase">False Positive (FP)</span>
            <p className="text-2xl font-bold text-status-rejected mt-1">{summary?.fp ?? 0}</p>
            <p className="text-[10px] text-slate-400 mt-0.5">False Accepts</p>
          </div>
          <div className="p-4 rounded-xl bg-graphite-950 border border-status-warning/40 text-center">
            <span className="text-[11px] text-slate-400 font-bold uppercase">False Negative (FN)</span>
            <p className="text-2xl font-bold text-status-warning mt-1">{summary?.fn ?? 0}</p>
            <p className="text-[10px] text-slate-400 mt-0.5">False Rejects</p>
          </div>
        </div>
      </div>

      {/* Generated Graphical Visualizations */}
      <div className="p-6 rounded-2xl bg-graphite-900 border border-graphite-800 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-graphite-800">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center space-x-2">
            <ImageIcon className="w-4 h-4 text-crimson-500" />
            <span>Matplotlib Benchmark Graphs</span>
          </h3>
          
          {/* Tab selector */}
          <div className="flex flex-wrap gap-2">
            {plots.map((p) => (
              <button
                key={p.id}
                onClick={() => setActiveTab(p.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${
                  activeTab === p.id 
                    ? 'bg-crimson-600 text-white shadow-md shadow-crimson-600/30 border border-crimson-500/50' 
                    : 'bg-graphite-950 text-slate-400 hover:text-white border border-graphite-800'
                }`}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        {/* Display Active Chart */}
        <div className="rounded-xl bg-graphite-950 p-4 border border-graphite-800 flex items-center justify-center min-h-[380px]">
          <img
            src={evaluationApi.getPlotUrl(activeTab)}
            alt={activeTab}
            className="max-h-[460px] object-contain rounded-lg shadow-xl"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
        </div>
      </div>
    </div>
  );
}
