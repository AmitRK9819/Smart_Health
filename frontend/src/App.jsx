import React, { useState } from 'react';
import { PHCGrid } from './components/PHCGrid';
import { RedistributionSankey } from './components/RedistributionSankey';
import { phcData } from './data/phcData';
import { Activity, GitMerge } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col md:flex-row">
      
      {/* Sidebar Navigation */}
      <div className="w-full md:w-64 bg-slate-900 text-slate-300 flex flex-col shadow-xl z-10 sticky top-0 md:h-screen">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold text-white leading-tight">District Health</h1>
          <p className="text-xs text-slate-400 mt-1 uppercase tracking-widest">Command Center</p>
        </div>
        
        <nav className="flex-1 p-4 flex flex-row md:flex-col gap-2 overflow-x-auto md:overflow-hidden">
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'overview' 
                ? 'bg-blue-600 text-white' 
                : 'hover:bg-slate-800 hover:text-white'
            }`}
          >
            <Activity className="h-5 w-5" />
            Stock Overview
          </button>
          
          <button
            onClick={() => setActiveTab('redistribution')}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'redistribution' 
                ? 'bg-blue-600 text-white' 
                : 'hover:bg-slate-800 hover:text-white'
            }`}
          >
            <GitMerge className="h-5 w-5" />
            Redistribution
          </button>
        </nav>
        
        <div className="p-4 border-t border-slate-800 text-xs text-slate-500 hidden md:block">
          System Update: Live<br/>
          Server: Connected
        </div>
      </div>

      {/* Main Content Area */}
      <main className="flex-1 p-4 md:p-8 overflow-y-auto w-full">
        {activeTab === 'overview' && <PHCGrid phcs={phcData} />}
        {activeTab === 'redistribution' && <RedistributionSankey phcs={phcData} />}
      </main>

    </div>
  );
}

export default App;
