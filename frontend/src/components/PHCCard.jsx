import React from 'react';
import { getPHCOverallStatus, getStockStatus, getStockHours } from '../utils/stockUtils';
import { StatusBadge } from './StatusAndStats';
import { MapPin, Clock, AlertTriangle } from 'lucide-react';

export const PHCCard = ({ phc, onClick }) => {
  const overallStatus = getPHCOverallStatus(phc.stockItems);
  
  // Find the items driving the worst status
  const criticalItems = phc.stockItems.filter(item => getStockStatus(item) === overallStatus);
  // Sort them by hours remaining (lowest first)
  const sortedCriticalItems = criticalItems.sort((a, b) => {
    return getStockHours(a.currentUnits, a.avgDailyConsumption) - getStockHours(b.currentUnits, b.avgDailyConsumption);
  });

  const worstItem = sortedCriticalItems[0];
  const hoursLeft = worstItem ? Math.round(getStockHours(worstItem.currentUnits, worstItem.avgDailyConsumption)) : null;

  return (
    <div 
      className="bg-white rounded-lg shadow-sm border border-slate-200 p-5 hover:shadow-md transition-shadow cursor-pointer flex flex-col h-full"
      onClick={() => onClick(phc)}
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 leading-tight">{phc.name}</h3>
          <div className="flex items-center text-sm text-slate-500 mt-1">
            <MapPin className="h-3.5 w-3.5 mr-1" />
            {phc.block}
          </div>
        </div>
        <StatusBadge status={overallStatus} />
      </div>

      <div className="mt-auto pt-4 border-t border-slate-100">
        {overallStatus !== 'healthy' ? (
          <div className="flex items-start gap-2">
            <AlertTriangle className={`h-4 w-4 mt-0.5 ${overallStatus === 'critical' ? 'text-red-500' : 'text-yellow-500'}`} />
            <div>
              <div className="text-sm font-medium text-slate-800">
                {worstItem.itemName}
              </div>
              <div className="flex items-center text-xs text-slate-500 mt-0.5">
                <Clock className="h-3 w-3 mr-1" />
                Est. {hoursLeft} hours remaining
              </div>
            </div>
          </div>
        ) : (
          <div className="text-sm text-slate-500 flex items-center">
            <Clock className="h-4 w-4 mr-1.5 text-green-500" />
            All stock levels healthy (&gt;72h)
          </div>
        )}
      </div>
    </div>
  );
};
