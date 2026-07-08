import React, { useState, useEffect } from 'react';
import { PHCGrid } from './components/PHCGrid';
import { RedistributionSankey } from './components/RedistributionSankey';
import { LoginPage } from './components/LoginPage';
import { phcData as initialPHCData } from './data/phcData';
import { Activity, GitMerge, LogOut, Wifi, WifiOff, RefreshCw, Shield } from 'lucide-react';

function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('kraft_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [activeTab, setActiveTab] = useState('overview');
  const [phcs, setPhcs] = useState(initialPHCData);
  const [isLive, setIsLive] = useState(false);
  const [lastSync, setLastSync] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchLiveData = async (showSpinner = false) => {
    if (showSpinner) setRefreshing(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/facility/');
      if (res.ok) {
        const data = await res.json();
        if (data && data.length > 0) {
          setPhcs(data);
          setIsLive(true);
          setLastSync(new Date().toLocaleTimeString());
        }
      } else {
        setIsLive(false);
      }
    } catch (err) {
      setIsLive(false);
    } finally {
      if (showSpinner) setTimeout(() => setRefreshing(false), 500);
    }
  };

  useEffect(() => {
    if (user) {
      fetchLiveData();
      const interval = setInterval(() => fetchLiveData(false), 3000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const handleLogin = (userData) => {
    localStorage.setItem('kraft_user', JSON.stringify(userData));
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('kraft_user');
    setUser(null);
  };

  const handleAddPHC = (newPHC) => {
    setPhcs([newPHC, ...phcs]);
  };

  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-[#f5f5f7] flex flex-col md:flex-row font-sans">
      
      {/* Sidebar Navigation */}
      <div className="w-full md:w-72 bg-[#111111] flex flex-col z-10 sticky top-0 md:h-screen text-white justify-between">
        <div>
          <div className="p-8 pb-8 flex flex-col items-center justify-center text-center mt-2">
            <div className="w-16 h-16 border-2 border-white flex items-center justify-center mb-6 transform rotate-45 shadow-[0_0_20px_rgba(255,255,255,0.15)]">
               <div className="transform -rotate-45 font-black tracking-[0.2em] text-sm">KRAFT</div>
            </div>
            <h1 className="text-xs font-semibold tracking-[0.25em] text-white leading-loose uppercase">District Health</h1>
            <p className="text-[10px] text-neutral-500 mt-1 uppercase tracking-[0.3em] font-light">Command Center</p>
          </div>
          
          <nav className="px-6 flex flex-row md:flex-col gap-2 overflow-x-auto md:overflow-hidden">
            <button
              onClick={() => setActiveTab('overview')}
              className={`flex items-center justify-center md:justify-start gap-4 px-4 py-3.5 text-xs font-bold uppercase tracking-[0.15em] transition-all whitespace-nowrap cursor-pointer rounded ${
                activeTab === 'overview' 
                  ? 'bg-neutral-800 text-white border-l-4 border-white shadow-lg' 
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900/50 border-l-4 border-transparent'
              }`}
            >
              <Activity className="h-4 w-4 shrink-0 text-red-500" />
              Overview
            </button>
            
            <button
              onClick={() => setActiveTab('redistribution')}
              className={`flex items-center justify-center md:justify-start gap-4 px-4 py-3.5 text-xs font-bold uppercase tracking-[0.15em] transition-all whitespace-nowrap cursor-pointer rounded ${
                activeTab === 'redistribution' 
                  ? 'bg-neutral-800 text-white border-l-4 border-white shadow-lg' 
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900/50 border-l-4 border-transparent'
              }`}
            >
              <GitMerge className="h-4 w-4 shrink-0 text-cyan-400" />
              Redistribution
            </button>
          </nav>
        </div>

        {/* Live Sync Badge & Officer Profile */}
        <div className="p-6 border-t border-neutral-800/80 bg-[#0c0c0c] flex flex-col gap-4">
          {/* Live Status Pill */}
          <div className="flex items-center justify-between px-3 py-2 bg-neutral-900 rounded border border-neutral-800 text-[10px]">
            <div className="flex items-center gap-2 font-mono uppercase font-bold">
              {isLive ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span className="text-emerald-400">Live Sync ON</span>
                </>
              ) : (
                <>
                  <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                  <span className="text-amber-400">Offline / Mock</span>
                </>
              )}
            </div>
            <button
              onClick={() => fetchLiveData(true)}
              title="Force Refresh"
              className="text-neutral-400 hover:text-white transition-colors cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>

          {/* Officer Profile & Logout */}
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="w-8 h-8 rounded bg-neutral-800 border border-neutral-700 flex items-center justify-center shrink-0">
                <Shield className="w-4 h-4 text-neutral-300" />
              </div>
              <div className="overflow-hidden">
                <div className="text-xs font-bold text-white truncate">{user.username}</div>
                <div className="text-[10px] text-neutral-500 font-mono truncate">{user.email}</div>
              </div>
            </div>

            <button
              onClick={handleLogout}
              title="Sign Out"
              className="p-2 text-neutral-400 hover:text-red-400 hover:bg-neutral-900 rounded transition-colors shrink-0 cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="flex-1 p-6 md:p-12 overflow-y-auto w-full max-w-7xl mx-auto">
        {/* Top bar warning if offline */}
        {!isLive && (
          <div className="mb-6 p-3 bg-amber-50 border-l-4 border-amber-500 text-amber-900 text-xs flex items-center justify-between shadow-sm rounded-r">
            <div className="flex items-center gap-2">
              <WifiOff className="w-4 h-4 text-amber-600 shrink-0" />
              <span>
                <strong>Offline Mode:</strong> Could not connect to live API (`http://localhost:8000`). Displaying static backup data. Start the FastAPI server to sync live stock across all apps.
              </span>
            </div>
            <button
              onClick={() => fetchLiveData(true)}
              className="px-3 py-1 bg-amber-200/80 hover:bg-amber-300 font-bold uppercase tracking-wider text-[10px] rounded transition-colors cursor-pointer shrink-0 ml-4"
            >
              Retry Connection
            </button>
          </div>
        )}

        {activeTab === 'overview' && <PHCGrid phcs={phcs} onAddPHC={handleAddPHC} />}
        {activeTab === 'redistribution' && <RedistributionSankey phcs={phcs} />}
      </main>

    </div>
  );
}

export default App;
