import React, { useMemo, useState } from 'react';
import { Sankey, Tooltip, ResponsiveContainer } from 'recharts';
import { suggestTransfers } from '../utils/suggestTransfers';

export const RedistributionSankey = ({ phcs }) => {
  const [selectedItem, setSelectedItem] = useState('All');
  
  const transfers = useMemo(() => suggestTransfers(phcs), [phcs]);

  const itemsWithTransfers = useMemo(() => {
    const items = new Set(transfers.map(t => t.itemName));
    return Array.from(items).sort();
  }, [transfers]);

  const chartData = useMemo(() => {
    let filteredTransfers = transfers;
    if (selectedItem !== 'All') {
      filteredTransfers = transfers.filter(t => t.itemName === selectedItem);
    }
    
    // Limit to max 10 links to avoid clutter
    filteredTransfers = filteredTransfers.slice(0, 10);

    const nodesMap = new Map();
    const links = [];

    // Assign node indices
    let nodeIndex = 0;
    const getNodeIndex = (name) => {
      if (!nodesMap.has(name)) {
        nodesMap.set(name, nodeIndex++);
      }
      return nodesMap.get(name);
    };

    filteredTransfers.forEach(t => {
      const sourceIdx = getNodeIndex(`${t.sourceName} (Surplus)`);
      const targetIdx = getNodeIndex(`${t.targetName} (Shortage)`);
      
      links.push({
        source: sourceIdx,
        target: targetIdx,
        value: t.quantity,
        payload: t // for tooltip
      });
    });

    const nodes = Array.from(nodesMap.keys()).map(name => ({ name }));

    return { nodes, links };
  }, [transfers, selectedItem]);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      if (data.payload) { // This is a link tooltip
        const t = data.payload;
        return (
          <div className="bg-white p-3 rounded shadow-lg border border-slate-200">
            <p className="font-semibold text-slate-800 mb-1">{t.itemName}</p>
            <p className="text-sm text-slate-600">From: <span className="font-medium">{t.sourceName}</span></p>
            <p className="text-sm text-slate-600">To: <span className="font-medium">{t.targetName}</span></p>
            <p className="text-sm text-slate-600 mt-1">Transfer: <span className="font-bold text-blue-600">{t.quantity} units</span></p>
            <p className="text-xs text-green-600 mt-1">+{t.hoursImpact} hours added to shortage PHC</p>
          </div>
        );
      }
      // This is a node tooltip
      return (
        <div className="bg-white p-2 rounded shadow border border-slate-200">
          <p className="font-medium text-slate-800">{data.name}</p>
          <p className="text-sm text-slate-600">Total volume: {data.value}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 flex flex-col h-[calc(100vh-8rem)]">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Suggested Resource Redistributions</h2>
          <p className="text-sm text-slate-500 mt-1">Automatically matching critical shortages with local surpluses</p>
        </div>
        
        <select
          className="block w-64 pl-3 pr-8 py-2 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          value={selectedItem}
          onChange={(e) => setSelectedItem(e.target.value)}
        >
          <option value="All">All Items (Top 10 Transfers)</option>
          {itemsWithTransfers.map(item => (
            <option key={item} value={item}>{item}</option>
          ))}
        </select>
      </div>

      {chartData.nodes.length === 0 ? (
        <div className="flex-1 flex items-center justify-center border-2 border-dashed border-slate-200 rounded-lg">
          <div className="text-slate-400">No redistribution suggestions available for selected criteria.</div>
        </div>
      ) : (
        <div className="flex-1 min-h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <Sankey
              data={chartData}
              node={{ stroke: '#0f172a', strokeWidth: 1 }}
              nodePadding={40}
              margin={{ left: 20, right: 20, top: 20, bottom: 20 }}
              link={{ stroke: '#94a3b8' }}
            >
              <Tooltip content={<CustomTooltip />} />
            </Sankey>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};
