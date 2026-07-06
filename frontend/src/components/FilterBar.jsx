import React from 'react';
import { Search, Filter, ArrowUpDown } from 'lucide-react';

export const FilterBar = ({ 
  searchTerm, setSearchTerm, 
  filterBlock, setFilterBlock, 
  filterStatus, setFilterStatus,
  sortBy, setSortBy,
  blocks
}) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200 mb-6 flex flex-col md:flex-row gap-4 items-center justify-between">
      
      <div className="relative w-full md:w-1/3">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-4 w-4 text-slate-400" />
        </div>
        <input
          type="text"
          className="block w-full pl-10 pr-3 py-2 border border-slate-300 rounded-md leading-5 bg-slate-50 placeholder-slate-400 focus:outline-none focus:bg-white focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="Search PHC name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="flex flex-col sm:flex-row w-full md:w-auto gap-4">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-400" />
          <select
            className="block w-full pl-3 pr-8 py-2 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            value={filterBlock}
            onChange={(e) => setFilterBlock(e.target.value)}
          >
            <option value="All">All Blocks</option>
            {blocks.map(block => (
              <option key={block} value={block}>{block}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <select
            className="block w-full pl-3 pr-8 py-2 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="All">All Statuses</option>
            <option value="critical">Critical</option>
            <option value="warning">Warning</option>
            <option value="healthy">Healthy</option>
          </select>
        </div>

        <div className="flex items-center gap-2 border-l pl-4 ml-2">
          <ArrowUpDown className="h-4 w-4 text-slate-400" />
          <select
            className="block w-full pl-3 pr-8 py-2 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="severity">Sort by Severity</option>
            <option value="name">Sort by Name</option>
            <option value="block">Sort by Block</option>
          </select>
        </div>
      </div>

    </div>
  );
};
