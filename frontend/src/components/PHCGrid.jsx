import React, { useState, useMemo } from 'react';
import { PHCCard } from './PHCCard';
import { FilterBar } from './FilterBar';
import { SummaryStats } from './StatusAndStats';
import { PHCDetailModal } from './PHCDetailModal';
import { getPHCOverallStatus } from '../utils/stockUtils';

export const PHCGrid = ({ phcs }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterBlock, setFilterBlock] = useState('All');
  const [filterStatus, setFilterStatus] = useState('All');
  const [sortBy, setSortBy] = useState('severity');
  const [selectedPHC, setSelectedPHC] = useState(null);

  const blocks = useMemo(() => {
    const blockSet = new Set(phcs.map(p => p.block));
    return Array.from(blockSet).sort();
  }, [phcs]);

  const filteredAndSortedPHCs = useMemo(() => {
    // Filter
    let result = phcs.filter(phc => {
      const matchesSearch = phc.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesBlock = filterBlock === 'All' || phc.block === filterBlock;
      const overallStatus = getPHCOverallStatus(phc.stockItems);
      const matchesStatus = filterStatus === 'All' || overallStatus === filterStatus;
      
      return matchesSearch && matchesBlock && matchesStatus;
    });

    // Sort
    result.sort((a, b) => {
      if (sortBy === 'name') {
        return a.name.localeCompare(b.name);
      }
      if (sortBy === 'block') {
        return a.block.localeCompare(b.block);
      }
      if (sortBy === 'severity') {
        const statusMap = { 'critical': 3, 'warning': 2, 'healthy': 1 };
        const statusA = statusMap[getPHCOverallStatus(a.stockItems)];
        const statusB = statusMap[getPHCOverallStatus(b.stockItems)];
        if (statusA !== statusB) {
          return statusB - statusA; // Critical first
        }
        return a.name.localeCompare(b.name); // Tie breaker
      }
      return 0;
    });

    return result;
  }, [phcs, searchTerm, filterBlock, filterStatus, sortBy]);

  return (
    <div className="flex flex-col h-full">
      <SummaryStats phcs={phcs} />
      
      <FilterBar 
        searchTerm={searchTerm} setSearchTerm={setSearchTerm}
        filterBlock={filterBlock} setFilterBlock={setFilterBlock}
        filterStatus={filterStatus} setFilterStatus={setFilterStatus}
        sortBy={sortBy} setSortBy={setSortBy}
        blocks={blocks}
      />

      {filteredAndSortedPHCs.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center p-12 bg-white rounded-lg border border-slate-200 border-dashed">
          <div className="text-slate-400 mb-2">No PHCs match your filters</div>
          <button 
            onClick={() => {
              setSearchTerm('');
              setFilterBlock('All');
              setFilterStatus('All');
            }}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Clear all filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredAndSortedPHCs.map(phc => (
            <PHCCard key={phc.id} phc={phc} onClick={setSelectedPHC} />
          ))}
        </div>
      )}

      <PHCDetailModal phc={selectedPHC} onClose={() => setSelectedPHC(null)} />
    </div>
  );
};
