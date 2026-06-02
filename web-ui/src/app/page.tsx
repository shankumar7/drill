"use client";

import React, { useEffect, useState } from "react";
import { Gauge } from "../components/Gauge";
import { Activity, Shield, Users, Camera, LayoutGrid, Settings, LogOut, ChevronRight, CheckCircle2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";

// ==========================================
// LAUNCH SCREEN COMPONENT
// ==========================================
function LaunchScreen({ onComplete }: { onComplete: () => void }) {
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState("ESTABLISHING SECURE CONNECTION...");

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer);
          setTimeout(onComplete, 800); // Wait a bit at 100% before transitioning
          return 100;
        }
        
        // Update status text based on progress
        if (prev === 25) setStatusText("INITIALIZING NEURAL ENGINE...");
        if (prev === 50) setStatusText("CALIBRATING CAMERA FEEDS...");
        if (prev === 75) setStatusText("SYSTEM READY. STAND BY...");

        // Ease out speed
        const increment = prev > 80 ? 2 : prev > 40 ? 5 : 8;
        return Math.min(100, prev + increment);
      });
    }, 150);

    return () => clearInterval(timer);
  }, [onComplete]);

  return (
    <motion.div 
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#030305]"
      initial={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
      transition={{ duration: 1.2, ease: "easeInOut" }}
    >
      {/* Subtle Background Glow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[120px]"></div>
      </div>

      <motion.div 
        className="relative flex flex-col items-center z-10 w-full max-w-md px-8"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 1, delay: 0.2 }}
      >
        {/* Pulsing Logo Circle */}
        <div className="relative w-32 h-32 mb-12 flex items-center justify-center">
          <motion.div 
            className="absolute inset-0 border border-blue-500/30 rounded-full"
            animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.div 
            className="absolute inset-0 border border-blue-400/50 rounded-full"
            animate={{ scale: [1, 1.2, 1], opacity: [0.8, 0, 0.8] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
          />
          <div className="w-24 h-24 bg-black rounded-full overflow-hidden border-2 border-white/10 shadow-[0_0_30px_rgba(59,130,246,0.3)] relative z-10 flex items-center justify-center">
            <Image src="/logo.jpeg" alt="Logo" width={96} height={96} className="object-cover" />
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold tracking-widest text-white mb-2 text-center uppercase">
          Military Drill
        </h1>
        <h2 className="text-sm font-medium tracking-[0.3em] text-blue-400 mb-12 text-center">
          ANALYSIS SYSTEM
        </h2>

        {/* Progress Bar Container */}
        <div className="w-full space-y-4">
          <div className="flex justify-between items-end px-1">
            <span className="text-[10px] font-mono text-slate-400 tracking-wider">
              {statusText}
            </span>
            <span className="text-xs font-mono text-blue-400 font-bold">
              {progress}%
            </span>
          </div>
          
          <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden relative">
            <motion.div 
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-600 to-cyan-400 rounded-full shadow-[0_0_10px_rgba(56,189,248,0.5)]"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ ease: "linear", duration: 0.15 }}
            />
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

// ==========================================
// MAIN DASHBOARD COMPONENT
// ==========================================
function Dashboard() {
  const [telemetry, setTelemetry] = useState({
    torso_posture: 0,
    heel_alignment: 0,
    foot_angle: 0,
    arm_alignment: 0,
    overall_score: 0,
    status: "Initializing...",
  });

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/telemetry");
    ws.onmessage = (event) => {
      try {
        setTelemetry(JSON.parse(event.data));
      } catch (e) {
        console.error("Error parsing telemetry:", e);
      }
    };
    return () => ws.close();
  }, []);

  return (
    <motion.div 
      className="min-h-screen flex flex-col font-sans"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1, delay: 0.5 }}
    >
      {/* Top Navigation Bar */}
      <header className="glass-header h-16 flex items-center justify-between px-6 lg:px-8 sticky top-0 z-40">
        <div className="flex items-center space-x-4">
          <div className="w-8 h-8 rounded-full overflow-hidden border border-white/20">
             <Image src="/logo.jpeg" alt="Logo" width={32} height={32} className="object-cover" />
          </div>
          <div className="h-4 w-px bg-white/10 hidden sm:block"></div>
          <h1 className="text-lg font-bold tracking-wide uppercase hidden sm:block">
            Drill <span className="text-blue-500 font-normal">Command</span>
          </h1>
        </div>
        
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-3 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            <span className="text-xs font-semibold text-green-400 tracking-wider">SYSTEM ONLINE</span>
          </div>
          <button className="text-slate-400 hover:text-white transition-colors">
            <Settings className="w-5 h-5" />
          </button>
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center border border-white/10 shadow-lg cursor-pointer">
            <span className="text-xs font-bold">OP</span>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar Navigation */}
        <aside className="w-20 lg:w-64 glass-panel border-y-0 border-l-0 hidden md:flex flex-col py-6 transition-all duration-300">
          <nav className="space-y-1 px-3 flex-1">
            <NavItem icon={<LayoutGrid />} label="Dashboard" active />
            <NavItem icon={<Camera />} label="Camera Feeds" />
            <NavItem icon={<Users />} label="Squad Analysis" />
            <NavItem icon={<Activity />} label="Metrics Log" />
          </nav>
          <div className="px-3">
            <NavItem icon={<LogOut />} label="Disconnect" danger />
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 p-4 lg:p-8 overflow-y-auto">
          <div className="max-w-[1600px] mx-auto space-y-8">
            
            {/* Header Section */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
              <div>
                <h2 className="text-3xl font-bold tracking-tight">Active Drill Session</h2>
                <p className="text-slate-400 mt-1 flex items-center space-x-2">
                  <span>Platoon Alpha</span>
                  <ChevronRight className="w-4 h-4 text-slate-600" />
                  <span className="text-blue-400">Mode: SAVDHAN</span>
                </p>
              </div>
              <div className="flex space-x-3">
                <button className="px-6 py-2.5 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 font-medium text-sm transition-all shadow-sm">
                  Generate Report
                </button>
                <button className="px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm transition-all shadow-[0_0_15px_rgba(37,99,235,0.4)] hover:shadow-[0_0_25px_rgba(37,99,235,0.6)]">
                  End Session
                </button>
              </div>
            </div>

            {/* Top Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
              <StatCard 
                title="Overall Score" 
                value={`${telemetry.overall_score}%`} 
                color="blue" 
                subtitle="Aggregated evaluation"
              />
              <div className="glass-panel rounded-2xl p-5 relative overflow-hidden sm:col-span-2 lg:col-span-2 flex items-center border-l-4 border-l-indigo-500">
                 <div className="flex-1">
                   <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-1">Current Status</h3>
                   <div className="flex items-center space-x-3">
                     <div className={`text-3xl font-bold ${telemetry.status === 'Excellent' ? 'text-green-400' : telemetry.status === 'Good' ? 'text-yellow-400' : 'text-red-400'}`}>
                       {telemetry.status}
                     </div>
                     {telemetry.status === 'Excellent' && <CheckCircle2 className="w-6 h-6 text-green-400" />}
                   </div>
                   <p className="text-sm text-slate-500 mt-2">Posture is maintained within acceptable thresholds.</p>
                 </div>
              </div>
              <StatCard 
                title="Active Cameras" 
                value="4/4" 
                color="emerald" 
                subtitle="All feeds healthy"
              />
            </div>

            {/* Video & Telemetry Grid */}
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
              
              {/* Left Video Area (Spans 8 cols) */}
              <div className="xl:col-span-8 space-y-6">
                
                {/* Main Camera (Cam 1) */}
                <div className="glass-panel rounded-2xl overflow-hidden p-1 bg-gradient-to-b from-white/5 to-transparent">
                  <div className="relative aspect-[16/9] bg-[#0a0a0c] rounded-xl overflow-hidden shadow-inner border border-white/5">
                    <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-lg text-xs font-bold text-white z-10 flex items-center space-x-2 border border-white/10 shadow-lg">
                      <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.8)]"></span>
                      <span className="tracking-wider">CAM 1 - PRIMARY FRONT</span>
                    </div>
                    {/* Targeting FastAPI MJPEG stream */}
                    <img 
                      src="http://localhost:8000/api/video_feed/0" 
                      alt="Primary Feed" 
                      className="w-full h-full object-cover opacity-90 hover:opacity-100 transition-opacity duration-500"
                      onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                    />
                    <div className="absolute inset-0 flex flex-col items-center justify-center -z-10 text-slate-700">
                      <Shield className="w-16 h-16 mb-4 opacity-20" />
                      <span className="text-sm tracking-widest font-mono">WAITING FOR SIGNAL...</span>
                    </div>
                  </div>
                </div>

                {/* Sub Cameras Row */}
                <div className="grid grid-cols-3 gap-4 lg:gap-6">
                  {[1, 2, 3].map((camIdx) => (
                    <div key={camIdx} className="glass-panel rounded-xl p-1 bg-white/[0.02]">
                      <div className="relative aspect-video bg-[#0a0a0c] rounded-lg overflow-hidden border border-white/5">
                        <div className="absolute top-2 left-2 bg-black/60 backdrop-blur-md px-2 py-1 rounded text-[10px] font-bold text-slate-300 z-10 tracking-wider">
                          CAM {camIdx + 1}
                        </div>
                        <img 
                          src={`http://localhost:8000/api/video_feed/${camIdx}`} 
                          alt={`Camera ${camIdx + 1}`} 
                          className="w-full h-full object-cover"
                          onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                        />
                         <div className="absolute inset-0 flex flex-col items-center justify-center -z-10 text-slate-800 text-[10px] font-mono">
                           <span>NO SIGNAL</span>
                         </div>
                      </div>
                    </div>
                  ))}
                </div>

              </div>

              {/* Right Telemetry Sidebar (Spans 4 cols) */}
              <div className="xl:col-span-4 flex flex-col space-y-6">
                <div className="glass-panel rounded-2xl p-6 flex-1 flex flex-col">
                  <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-white/5">
                    <Activity className="w-5 h-5 text-blue-400" />
                    <h2 className="text-lg font-semibold tracking-wide">Live Telemetry</h2>
                  </div>
                  
                  <div className="flex-1 grid grid-cols-2 gap-4 lg:grid-cols-2 xl:grid-cols-1 content-start space-y-0 xl:space-y-4">
                    <TelemetryGaugeCard label="Torso Posture" value={telemetry.torso_posture} />
                    <TelemetryGaugeCard label="Heel Alignment" value={telemetry.heel_alignment} />
                    <TelemetryGaugeCard label="Foot Angle" value={telemetry.foot_angle} />
                    <TelemetryGaugeCard label="Arm Alignment" value={telemetry.arm_alignment} />
                  </div>
                </div>
              </div>

            </div>
          </div>
        </main>
      </div>
    </motion.div>
  );
}

// ==========================================
// HELPER COMPONENTS
// ==========================================

function NavItem({ icon, label, active = false, danger = false }: any) {
  return (
    <a href="#" className={`
      flex items-center space-x-3 px-3 lg:px-4 py-3 rounded-xl transition-all group
      ${active ? 'bg-blue-600/10 text-blue-400 relative' : 'text-slate-400 hover:text-white hover:bg-white/5'}
      ${danger ? 'mt-auto text-red-400 hover:text-red-300 hover:bg-red-500/10' : ''}
    `}>
      {active && (
        <motion.div layoutId="nav-indicator" className="absolute left-0 top-2 bottom-2 w-1 bg-blue-500 rounded-r-full" />
      )}
      <div className={`w-5 h-5 ${active ? 'text-blue-400' : 'text-slate-500 group-hover:text-slate-300'} transition-colors`}>
        {icon}
      </div>
      <span className="font-medium text-sm hidden lg:block tracking-wide">{label}</span>
    </a>
  );
}

function StatCard({ title, value, subtitle, color }: any) {
  const colorMap: Record<string, string> = {
    blue: "border-l-blue-500 text-blue-400",
    indigo: "border-l-indigo-500 text-indigo-400",
    emerald: "border-l-emerald-500 text-emerald-400",
  };

  return (
    <div className={`glass-panel rounded-2xl p-5 border-l-4 ${colorMap[color] || 'border-l-slate-500'} relative overflow-hidden group`}>
      <div className={`absolute -right-4 -top-4 w-24 h-24 bg-${color}-500/5 rounded-full blur-2xl group-hover:bg-${color}-500/10 transition-colors`}></div>
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-1">{title}</h3>
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      <p className="text-xs text-slate-500">{subtitle}</p>
    </div>
  );
}

function TelemetryGaugeCard({ label, value }: { label: string, value: number }) {
  return (
    <div className="bg-[#0a0a0c] rounded-xl border border-white/5 p-4 flex items-center justify-between hover:border-white/10 transition-colors">
      <div className="flex-1">
        <h4 className="text-sm font-medium text-slate-300 tracking-wide">{label}</h4>
        <div className="mt-2 w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
          <motion.div 
            className={`h-full rounded-full ${value >= 80 ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : value >= 50 ? 'bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.6)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]'}`}
            initial={{ width: 0 }}
            animate={{ width: `${value}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>
      <div className="w-16 flex justify-end ml-4">
        <span className="text-xl font-bold text-white font-mono">{value}<span className="text-xs text-slate-500 ml-0.5">%</span></span>
      </div>
    </div>
  );
}

// ==========================================
// APP ENTRY POINT
// ==========================================
export default function App() {
  const [isLaunching, setIsLaunching] = useState(true);

  return (
    <AnimatePresence mode="wait">
      {isLaunching ? (
        <LaunchScreen key="launcher" onComplete={() => setIsLaunching(false)} />
      ) : (
        <Dashboard key="dashboard" />
      )}
    </AnimatePresence>
  );
}
