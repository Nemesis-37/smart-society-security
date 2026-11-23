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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-navy-800">
        <div>
          <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2">
            <FileText className="w-6 h-6 text-blue-500" />
            <span>Gate Entry & Access Audit Logs</span>
          </h2>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Tamper-resistant SQLite record of optical gate verification decisions ({total} logged events)
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="p-2.5 rounded-xl bg-navy-900 hover:bg-navy-800 border border-navy-700 text-slate-300 transition-colors self-start sm:self-auto"
          title="Refresh logs"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-navy-900/60 p-3.5 rounded-2xl border border-navy-800">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by Resident Name or ID..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-navy-950 border border-navy-700 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
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
            className="px-3 py-2 rounded-xl bg-navy-950 border border-navy-700 text-xs text-slate-300 focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="">All Verification Statuses</option>
            <option value="ENTRY ALLOWED">ENTRY ALLOWED (Resident)</option>
            <option value="ENTRY REJECTED">ENTRY REJECTED (Unknown)</option>
          </select>
        </div>
      </div>

      {/* Logs Table / List */}
      {loading ? (
        <div className="p-16 text-center rounded-2xl bg-navy-900/60 border border-navy-800">
          <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-3" />
          <p className="text-sm font-medium text-slate-400">Loading audit log records from SQLite...</p>
        </div>
      ) : logs.length === 0 ? (
        <div className="p-16 text-center rounded-2xl bg-navy-900/60 border border-navy-800 max-w-2xl mx-auto my-8">
          <div className="w-16 h-16 rounded-2xl bg-navy-800 border border-navy-700 flex items-center justify-center mx-auto mb-4 text-slate-400">
            <Inbox size={32} />
          </div>
          <h3 className="text-base font-bold text-white tracking-tight">
            No Entry Records Matching Filter
          </h3>
          <p className="text-xs text-slate-400 mt-2 max-w-sm mx-auto leading-relaxed">
            {search || statusFilter
              ? 'Try adjusting your search query or filter selection.'
              : 'Audit entries are automatically logged when entrant faces are processed in the Live Security Gate camera session.'}
          </p>
        </div>
      ) : (
        <div className="rounded-2xl bg-navy-900/80 border border-navy-800 shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-navy-950/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-navy-800">
                <tr>
                  <th className="py-3.5 px-4 font-mono">Log ID</th>
                  <th className="py-3.5 px-4">Entrant Name</th>
                  <th className="py-3.5 px-4 font-mono">Resident ID</th>
                  <th className="py-3.5 px-4">Decision</th>
                  <th className="py-3.5 px-4 font-mono">Face Distance</th>
                  <th className="py-3.5 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-800/60 text-slate-200">
                {logs.map((log) => {
                  const isAllowed = log.decision === 'ENTRY ALLOWED';
                  return (
                    <tr key={log.id} className="hover:bg-navy-800/40 transition-colors">
                      <td className="py-3 px-4 font-mono text-slate-400">#{log.id}</td>
                      <td className="py-3 px-4 font-bold text-white">
                        <div className="flex items-center space-x-2">
                          <User size={14} className={isAllowed ? 'text-emerald-400' : 'text-rose-400'} />
                          <span>{log.name}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 font-mono">
                        {log.resident_id ? (
                          <span className="text-cyan-400 font-semibold">{log.resident_id}</span>
                        ) : (
                          <span className="text-slate-500 italic">N/A</span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={isAllowed ? 'success' : 'danger'} size="xs">
                          {log.decision}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 font-mono">
                        {log.distance ? `${log.distance.toFixed(4)}` : 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                        {log.timestamp}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination Strip */}
          <div className="p-3.5 bg-navy-950/80 border-t border-navy-800 flex items-center justify-between text-xs text-slate-400">
            <span>
              Showing {page * limit + 1}–{Math.min((page + 1) * limit, total)} of {total} events
            </span>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="p-1.5 rounded-lg bg-navy-900 border border-navy-700 text-slate-300 hover:text-white disabled:opacity-40 transition-colors"
                title="Previous page"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="font-mono text-slate-300">
                {page + 1} / {totalPages || 1}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                className="p-1.5 rounded-lg bg-navy-900 border border-navy-700 text-slate-300 hover:text-white disabled:opacity-40 transition-colors"
                title="Next page"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
