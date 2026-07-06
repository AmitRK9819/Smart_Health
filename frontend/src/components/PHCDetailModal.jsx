import React from 'react';
import { X } from 'lucide-react';
import { getStockStatus, getStockHours } from '../utils/stockUtils';
import { StatusBadge } from './StatusAndStats';

export const PHCDetailModal = ({ phc, onClose }) => {
  if (!phc) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-3xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div>
            <h2 className="text-xl font-bold text-slate-900">{phc.name}</h2>
            <div className="text-sm text-slate-500 mt-1">{phc.block} Block</div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto">
          <h3 className="text-sm font-semibold text-slate-900 uppercase tracking-wider mb-4">Stock Inventory</h3>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 border border-slate-200 rounded-lg">
              <thead className="bg-slate-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Item Name</th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Current Stock</th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Daily Avg</th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Est. Hours Left</th>
                  <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {phc.stockItems.map((item, idx) => {
                  const status = getStockStatus(item);
                  const hours = Math.round(getStockHours(item.currentUnits, item.avgDailyConsumption));
                  
                  // Row background for critical items
                  const rowClass = status === 'critical' ? 'bg-red-50' : status === 'warning' ? 'bg-yellow-50' : '';

                  return (
                    <tr key={idx} className={rowClass}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{item.itemName}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700 text-right">{item.currentUnits.toLocaleString()}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700 text-right">{item.avgDailyConsumption}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700 text-right font-medium">
                        {hours === Infinity ? '∞' : hours}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <StatusBadge status={status} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          
          <div className="mt-4 text-xs text-slate-500 flex justify-end">
            Last updated: {new Date(phc.lastUpdated).toLocaleString()}
          </div>
        </div>

      </div>
    </div>
  );
};
