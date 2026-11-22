import React from 'react';
import { FileText, Inbox, ShieldCheck, Clock } from 'lucide-react';
import Badge from '../components/common/Badge';

export default function EntryLogs() {
  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-navy-800">
        <div>
          <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2">
            <FileText className="w-6 h-6 text-blue-500" />
            <span>Gate Entry & Access Logs</span>
          </h2>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Audit trail of verified resident admissions and security rejections
          </p>
        </div>

        <Badge variant="neutral" size="sm">
          Live Audit Mode
        </Badge>
      </div>

      {/* Honest Empty State */}
      <div className="p-16 text-center rounded-2xl bg-navy-900/60 border border-navy-800 shadow-xl max-w-2xl mx-auto my-12">
        <div className="w-16 h-16 rounded-2xl bg-navy-800 border border-navy-700 flex items-center justify-center mx-auto mb-4 text-slate-400">
          <Inbox size={32} />
        </div>
        <h3 className="text-lg font-bold text-white tracking-tight">
          No Access Logs Recorded Yet
        </h3>
        <p className="text-xs md:text-sm text-slate-400 mt-2 max-w-md mx-auto leading-relaxed">
          The system strictly displays genuine operational records. Gate entry events are generated when the Live Security Gate camera active session processes entrant faces in real time (Phase 5).
        </p>

        <div className="mt-6 pt-6 border-t border-navy-800 text-xs text-slate-500 flex items-center justify-center space-x-4">
          <span className="flex items-center space-x-1">
            <ShieldCheck size={14} className="text-emerald-400" />
            <span>Zero Fabricated Logs</span>
          </span>
          <span className="flex items-center space-x-1">
            <Clock size={14} className="text-cyan-400" />
            <span>Awaiting Live Gate Session</span>
          </span>
        </div>
      </div>
    </div>
  );
}
