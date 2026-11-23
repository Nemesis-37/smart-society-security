import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Search, 
  Filter, 
  RefreshCw, 
  ShieldCheck, 
  ShieldAlert, 
  Clock, 
  Inbox, 
  ChevronLeft, 
  ChevronRight,
  User,
  Calendar
} from 'lucide-react';
import Badge from '../components/common/Badge';
import Alert from '../components/common/Alert';
import { logsApi } from '../services/api';

export default function EntryLogs() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const limit = 15;

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLogs();
  }, [page, statusFilter]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = {
        limit,
        offset: page * limit,
      };
      if (search.trim()) params.search = search.trim();
      if (statusFilter) params.status = statusFilter;

      const res = await logsApi.getLogs(params);
      setLogs(res.data.items);
      setTotal(res.data.total);
      setError(null);
    } catch {
      setError('Could not retrieve access logs from FastAPI backend.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(0);
    fetchLogs();
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-graphite-800">
        <div>
          <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2 font-mono">
            <FileText className="w-6 h-6 text-crimson-500" />
            <span>ACCESS AUDIT LOGS</span>
          </h2>
          <p className="text-xs md:text-sm text-slate-400 mt-1 font-mono">
            Tamper-resistant SQLite record of optical gate verification decisions ({total} logged events)
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="p-2.5 rounded-xl bg-graphite-900 hover:bg-graphite-800 border border-graphite-700 text-slate-300 transition-colors self-start sm:self-auto"
          title="Refresh logs"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-graphite-900 p-3.5 rounded-2xl border border-graphite-800">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by Resident Name or ID..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-graphite-950 border border-graphite-800 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-crimson-600"
          />
        </form>

        <div className="flex items-center space-x-2">
          <Filter size={14} className="text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(0);
            }}
            className="px-3 py-2 rounded-xl bg-graphite-950 border border-graphite-800 text-xs font-mono text-slate-300 focus:outline-none focus:border-crimson-600 cursor-pointer"
          >
            <option value="">ALL VERIFICATION STATUSES</option>
            <option value="ENTRY ALLOWED">ENTRY ALLOWED (Resident)</option>
            <option value="ENTRY REJECTED">ENTRY REJECTED (Intruder/Unknown)</option>
          </select>
        </div>
      </div>

      {/* Logs Table */}
      <div className="rounded-2xl bg-graphite-900 border border-graphite-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-sans">
            <thead className="bg-graphite-950 border-b border-graphite-800 text-slate-400 uppercase tracking-wider font-mono text-[10px]">
              <tr>
                <th className="px-5 py-3.5">Timestamp</th>
                <th className="px-5 py-3.5">Resident ID</th>
                <th className="px-5 py-3.5">Name / Identity</th>
                <th className="px-5 py-3.5">Face Distance</th>
                <th className="px-5 py-3.5">Confidence</th>
                <th className="px-5 py-3.5 text-right">Verification Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-graphite-800/60">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-5 py-12 text-center text-slate-400 font-mono">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-crimson-500" />
                    <span>Loading audit records...</span>
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-5 py-12 text-center text-slate-400 font-mono">
                    No access log events recorded matching the criteria.
                  </td>
                </tr>
              ) : (
                logs.map((log) => {
                  const isAllowed = log.access_status === 'ENTRY ALLOWED';
                  return (
                    <tr key={log.id} className="hover:bg-graphite-850/50 transition-colors">
                      <td className="px-5 py-3.5 font-mono text-slate-400 text-[11px]">
                        {log.timestamp}
                      </td>
                      <td className="px-5 py-3.5">
                        <span className="font-mono font-bold text-slate-200">
                          {log.resident_id || 'UNKNOWN'}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 font-semibold text-white">
                        {log.name || 'Unknown Face'}
                      </td>
                      <td className="px-5 py-3.5 font-mono text-slate-400">
                        {log.distance !== null && log.distance !== undefined ? log.distance.toFixed(4) : 'N/A'}
                      </td>
                      <td className="px-5 py-3.5 font-mono">
                        <span className={isAllowed ? 'text-status-allowed font-bold' : 'text-slate-400'}>
                          {log.confidence ? `${(log.confidence * 100).toFixed(1)}%` : '0.0%'}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <Badge variant={isAllowed ? 'allowed' : 'rejected'} size="xs">
                          {log.access_status}
                        </Badge>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 bg-graphite-950 border-t border-graphite-800 flex items-center justify-between text-xs font-mono">
          <span className="text-slate-400">
            PAGE {totalPages === 0 ? 0 : page + 1} OF {totalPages || 1} ({total} EVENTS)
          </span>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="p-1.5 rounded-lg bg-graphite-850 hover:bg-graphite-800 text-slate-300 disabled:opacity-30 border border-graphite-700"
            >
              <ChevronLeft size={16} />
            </button>
            <button
              onClick={() => setPage((p) => (p + 1 < totalPages ? p + 1 : p))}
              disabled={page + 1 >= totalPages}
              className="p-1.5 rounded-lg bg-graphite-850 hover:bg-graphite-800 text-slate-300 disabled:opacity-30 border border-graphite-700"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
