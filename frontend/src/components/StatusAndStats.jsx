import React from 'react';
import { getPHCOverallStatus } from '../utils/stockUtils';

export const StatusBadge = ({ status }) => {
  const colors = {
    healthy: "bg-green-100 text-green-800 border-green-200",
    warning: "bg-yellow-100 text-yellow-800 border-yellow-200",
    critical: "bg-red-100 text-red-800 border-red-200"
  };

  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border uppercase tracking-wider ${colors[status]}`}>
      {status}
    </span>
  );
};

export const SummaryStats = ({ phcs }) => {
  const counts = { total: phcs.length, healthy: 0, warning: 0, critical: 0 };
  
  phcs.forEach(phc => {
    const status = getPHCOverallStatus(phc.stockItems);
    counts[status]++;
  });

  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
        <div className="text-sm font-medium text-slate-500">Total PHCs</div>
        <div className="mt-1 text-2xl font-semibold text-slate-900">{counts.total}</div>
      </div>
      <div className="bg-white rounded-lg shadow-sm border border-green-200 p-4 border-l-4 border-l-green-500">
        <div className="text-sm font-medium text-green-600">Healthy</div>
        <div className="mt-1 text-2xl font-semibold text-slate-900">{counts.healthy}</div>
      </div>
      <div className="bg-white rounded-lg shadow-sm border border-yellow-200 p-4 border-l-4 border-l-yellow-500">
        <div className="text-sm font-medium text-yellow-600">Warning</div>
        <div className="mt-1 text-2xl font-semibold text-slate-900">{counts.warning}</div>
      </div>
      <div className="bg-white rounded-lg shadow-sm border border-red-200 p-4 border-l-4 border-l-red-500">
        <div className="text-sm font-medium text-red-600">Critical</div>
        <div className="mt-1 text-2xl font-semibold text-slate-900">{counts.critical}</div>
      </div>
    </div>
  );
};
