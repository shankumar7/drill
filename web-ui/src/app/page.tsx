"use client";

import React, { useEffect, useState } from "react";
import { Gauge } from "../components/Gauge";
import { Activity, Shield, Users, Camera, LayoutGrid, Settings, LogOut, ChevronRight, CheckCircle2, ChevronRightCircle, Plus } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";

// ==========================================
// 1. LAUNCH SCREEN (System Boot Sequence)
// ==========================================
function LaunchScreen({ onComplete }: { onComplete: () => void }) {
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  
  const bootSequence = [
    "INIT KERNEL MODULES... OK",
    "ALLOCATING NEURAL MEMORY (4096 MB)... OK",
    "LOADING YOLO INFERENCE ENGINE... V8.1 ACTIVE",
    "ESTABLISHING CAMERA HOOKS... /dev/video0 DETECTED",
    "CALIBRATING POSE ESTIMATION HEURISTICS...",
    "SYNCING BIOMECHANICAL MODELS... OK",
    "SYSTEM SECURE. READY FOR DEPLOYMENT."
  ];

  useEffect(() => {
    let currentLog = 0;
    const logInterval = setInterval(() => {
      if (currentLog < bootSequence.length) {
        setLogs(prev => [...prev, bootSequence[currentLog]]);
        currentLog++;
      }
    }, 450);

    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer);
          clearInterval(logInterval);
          setTimeout(onComplete, 800);
          return 100;
        }
        const increment = prev > 80 ? 1.5 : prev > 40 ? 3 : 5;
        return Math.min(100, prev + increment);
      });
    }, 100);

    return () => { clearInterval(timer); clearInterval(logInterval); };
  }, [onComplete]);

  return (
    <motion.div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#010101] overflow-hidden font-sans selection:bg-blue-500/30"
      initial={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 1.05, filter: "blur(20px)" }}
      transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
    >
      {/* Background Layer: Tech Grid & Vignette */}
      <div className="absolute inset-0 pointer-events-none z-0 flex items-center justify-center">
        <div 
          className="absolute inset-0 opacity-[0.04]" 
          style={{ 
            backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, 
            backgroundSize: '30px 30px' 
          }}
        ></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,#010101_80%)]"></div>
        <div className="w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[120px]"></div>
      </div>
      
      <div className="relative z-10 w-full max-w-4xl px-8 flex flex-col md:flex-row items-center gap-16 mt-[-5vh]">
        
        {/* Left Side: Cinematic Logo */}
        <div className="relative flex flex-col items-center">
          <div className="relative w-72 h-72 flex items-center justify-center">
            {/* Radar / Scanning Effect */}
            <motion.div 
              className="absolute inset-0 border border-blue-500/20 rounded-full" 
              animate={{ scale: [1, 1.5, 1], opacity: [0.2, 0, 0.2] }} 
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }} 
            />
            <motion.div 
              className="absolute inset-0 border border-emerald-400/20 rounded-full" 
              animate={{ scale: [1, 1.3, 1], opacity: [0.4, 0, 0.4] }} 
              transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }} 
            />
            
            {/* Logo Container */}
            <motion.div 
              className="w-56 h-56 bg-[#030305] rounded-full overflow-hidden border-[4px] border-white/5 shadow-[0_0_60px_rgba(59,130,246,0.3)] relative z-10"
              initial={{ scale: 0.8, opacity: 0, rotate: -10 }}
              animate={{ scale: 1, opacity: 1, rotate: 0 }}
              transition={{ duration: 1.5, ease: "easeOut" }}
            >
              <div className="absolute inset-0 bg-blue-500/10 mix-blend-overlay z-20"></div>
              {/* Laser Scan Line */}
              <motion.div 
                className="absolute left-0 right-0 h-[2px] bg-blue-400 shadow-[0_0_10px_rgba(96,165,250,1)] z-30"
                animate={{ top: ['0%', '100%', '0%'] }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
              />
              <Image src="/logo.jpeg" alt="System Logo" fill className="object-cover opacity-90 saturate-0" />
            </motion.div>
          </div>
        </div>

        {/* Right Side: Typography & Boot Sequence */}
        <div className="flex-1 w-full flex flex-col justify-center">
          <motion.div 
            initial={{ x: 30, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 1, delay: 0.4 }}
          >
            <h2 className="text-xs font-bold tracking-[0.4em] text-blue-500 mb-2 uppercase flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-blue-500 animate-pulse rounded-full"></span>
              <span>Boot Sequence Initiated</span>
            </h2>
            <h1 className="text-5xl font-black tracking-tight text-white mb-2 leading-none uppercase">
              Military Drill
            </h1>
            <h1 className="text-5xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 mb-10 leading-none">
              Analysis System
            </h1>
          </motion.div>

          {/* Progress Bar Container */}
          <motion.div 
            className="w-full space-y-3 mb-8"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1, delay: 0.7 }}
          >
            <div className="flex justify-between items-end">
              <span className="text-xs font-mono text-slate-400 tracking-widest uppercase">System Loading</span>
              <span className="text-sm font-mono text-white font-bold">{Math.floor(progress)}%</span>
            </div>
            <div className="h-2 w-full bg-[#111] rounded overflow-hidden relative border border-white/10">
              <motion.div 
                className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-600 to-emerald-400" 
                initial={{ width: 0 }} animate={{ width: `${progress}%` }} 
                transition={{ ease: "linear", duration: 0.1 }} 
              />
              {/* Shine effect on progress bar */}
              <motion.div 
                 className="absolute top-0 bottom-0 w-20 bg-white/20 skew-x-[-20deg]"
                 animate={{ left: ['-100%', '200%'] }}
                 transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              />
            </div>
          </motion.div>

          {/* Terminal Logs */}
          <div className="h-32 bg-[#050508] border border-white/5 rounded-lg p-4 overflow-hidden shadow-inner relative">
             <div className="absolute inset-0 bg-[linear-gradient(rgba(0,0,0,0)_50%,rgba(0,0,0,0.25)_50%)] bg-[length:100%_4px] pointer-events-none z-10"></div>
             <div className="flex flex-col space-y-1 relative z-0">
               {logs.map((log, index) => (
                 <motion.div 
                   key={index} 
                   initial={{ opacity: 0, x: -10 }} 
                   animate={{ opacity: 1, x: 0 }}
                   className={`text-[10px] font-mono tracking-wider ${index === logs.length - 1 ? 'text-emerald-400' : 'text-slate-500'}`}
                 >
                   {`> ${log}`}
                 </motion.div>
               ))}
               {progress < 100 && (
                 <motion.div 
                   animate={{ opacity: [1, 0] }} transition={{ repeat: Infinity, duration: 0.5 }}
                   className="text-[10px] font-mono text-slate-500 mt-1"
                 >
                   _
                 </motion.div>
               )}
             </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// ==========================================
// 2. ONBOARDING INFO SCREEN
// ==========================================
function OnboardingScreen({ onNext }: { onNext: () => void }) {
  return (
    <motion.div 
      className="fixed inset-0 z-40 flex items-center justify-center bg-[#020203] overflow-hidden"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, x: -50, filter: "blur(10px)" }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      {/* Dynamic Immersive Background */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Glows */}
        <div className="absolute top-0 right-0 w-[1000px] h-[1000px] bg-blue-600/10 rounded-full blur-[150px] transform translate-x-1/3 -translate-y-1/3"></div>
        <div className="absolute bottom-0 left-0 w-[800px] h-[800px] bg-emerald-600/10 rounded-full blur-[150px] transform -translate-x-1/3 translate-y-1/3"></div>
        
        {/* Tech Grid Overlay */}
        <div 
          className="absolute inset-0 opacity-[0.03]" 
          style={{ 
            backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, 
            backgroundSize: '40px 40px' 
          }}
        ></div>

        {/* Animated Particles / Stars */}
        {Array.from({ length: 20 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute bg-white rounded-full opacity-20"
            style={{
              width: Math.random() * 3 + 1 + 'px',
              height: Math.random() * 3 + 1 + 'px',
              left: Math.random() * 100 + '%',
              top: Math.random() * 100 + '%',
            }}
            animate={{
              y: [0, Math.random() * -100 - 50],
              opacity: [0, 0.5, 0],
            }}
            transition={{
              duration: Math.random() * 5 + 5,
              repeat: Infinity,
              ease: "linear",
              delay: Math.random() * 5,
            }}
          />
        ))}
      </div>
      
      {/* Decorative Corner Accents */}
      <div className="absolute top-8 left-8 w-16 h-16 border-t-2 border-l-2 border-blue-500/50 opacity-50"></div>
      <div className="absolute bottom-8 right-8 w-16 h-16 border-b-2 border-r-2 border-emerald-500/50 opacity-50"></div>

      <div className="glass-panel p-12 lg:p-16 rounded-3xl max-w-5xl w-full mx-6 relative z-10 border border-white/10 shadow-[0_30px_100px_-15px_rgba(0,0,0,0.9)] bg-gradient-to-br from-[#0c0c10]/80 to-[#050508]/95">
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3, duration: 1, ease: "easeOut" }}>
          
          <div className="flex items-center space-x-4 mb-6">
            <Shield className="w-8 h-8 text-blue-500 opacity-80" />
            <h3 className="text-sm font-bold text-slate-400 tracking-[0.3em] uppercase">
              Simulation Development Division (SDD), MCEME
            </h3>
          </div>

          <h1 className="text-5xl lg:text-[5rem] font-black text-white tracking-tight mb-8 leading-[1.1]">
            Military Drill <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-emerald-400 drop-shadow-[0_0_15px_rgba(56,189,248,0.3)]">
              Analysis System.
            </span>
          </h1>
          
          <div className="flex items-center space-x-4 mb-10">
            <div className="w-32 h-1 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full"></div>
            <div className="w-4 h-1 bg-emerald-500 rounded-full"></div>
            <div className="w-2 h-1 bg-emerald-500 rounded-full opacity-50"></div>
          </div>

          <p className="text-lg lg:text-xl text-slate-400 max-w-3xl leading-relaxed mb-14 font-light">
            A professional evaluation suite designed for rigorous posture and alignment tracking. 
            Initialize the workspace to begin real-time, multi-camera drill compliance assessment powered by state-of-the-art neural engines.
          </p>

          <div className="flex items-center space-x-8">
            <button 
              onClick={onNext}
              className="group relative overflow-hidden flex items-center justify-center space-x-4 bg-white text-black px-10 py-5 rounded-full font-bold text-lg hover:scale-[1.02] active:scale-95 transition-all shadow-[0_0_30px_rgba(255,255,255,0.15)] hover:shadow-[0_0_40px_rgba(255,255,255,0.3)]"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-white via-slate-100 to-white opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <span className="relative z-10 tracking-wide uppercase">Initialize Workspace</span>
              <ChevronRightCircle className="relative z-10 w-6 h-6 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

        </motion.div>
      </div>
    </motion.div>
  );
}

// ==========================================
// 3. CONFIGURATION SCREEN
// ==========================================
function ConfigScreen({ onStart }: { onStart: (workflow: string[]) => void }) {
  const [selectedAction, setSelectedAction] = useState("Savadhan");
  const [workflow, setWorkflow] = useState<string[]>([]);

  const actions = ["Savadhan", "Vishram", "Salute", "Turn Right", "Turn Left", "About Turn"];

  const handleAdd = () => {
    setWorkflow([...workflow, selectedAction]);
  };

  return (
    <motion.div 
      className="fixed inset-0 z-30 flex items-center justify-center bg-[#050505]"
      initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <div className="glass-panel p-10 rounded-3xl max-w-2xl w-full mx-6 border border-white/10 shadow-2xl">
        <h2 className="text-3xl font-bold text-white mb-2 tracking-tight">Configure Drill Workflow</h2>
        <p className="text-slate-400 mb-8">Select the actions to include in this multi-camera evaluation session.</p>

        <div className="flex space-x-4 mb-8">
          <select 
            className="flex-1 bg-black/50 border border-white/20 text-white rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500 transition-colors text-lg"
            value={selectedAction}
            onChange={(e) => setSelectedAction(e.target.value)}
          >
            {actions.map(action => <option key={action} value={action}>{action}</option>)}
          </select>
          <button 
            onClick={handleAdd}
            className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-medium flex items-center justify-center space-x-2 transition-all shadow-[0_0_15px_rgba(37,99,235,0.4)]"
          >
            <Plus className="w-5 h-5" />
            <span>Add Action</span>
          </button>
        </div>

        <div className="mb-8">
          <h3 className="text-sm font-semibold tracking-wider text-slate-500 uppercase mb-3">Current Workflow Queue</h3>
          <div className="min-h-[120px] bg-black/40 border border-white/5 rounded-xl p-4 flex flex-wrap gap-2 items-start content-start">
            {workflow.length === 0 ? (
              <span className="text-slate-600 text-sm m-auto">No actions queued. Add an action above.</span>
            ) : (
              workflow.map((action, idx) => (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
                  key={idx} 
                  className="bg-white/10 border border-white/20 px-3 py-1.5 rounded-lg text-sm font-medium text-blue-100 flex items-center space-x-2"
                >
                  <span>{action}</span>
                  {idx < workflow.length - 1 && <ChevronRight className="w-3 h-3 text-slate-500 ml-1" />}
                </motion.div>
              ))
            )}
          </div>
        </div>

        <button 
          onClick={() => onStart(workflow)}
          disabled={workflow.length === 0}
          className={`w-full py-4 rounded-xl font-bold text-lg transition-all ${workflow.length > 0 ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.4)]' : 'bg-slate-800 text-slate-500 cursor-not-allowed'}`}
        >
          START SQUAD EVALUATION
        </button>
      </div>
    </motion.div>
  );
}

// ==========================================
// 4. MAIN DASHBOARD (Multi-Camera)
// ==========================================
function Dashboard({ activeWorkflow }: { activeWorkflow: string[] }) {
  const [telemetry, setTelemetry] = useState({
    torso_posture: 0,
    heel_alignment: 0,
    foot_angle: 0,
    arm_alignment: 0,
    overall_score: 0,
    status: "Initializing...",
  });

  const currentMode = activeWorkflow.length > 0 ? activeWorkflow[0].toUpperCase() : "SAVDHAN";

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/telemetry");
    ws.onmessage = (event) => {
      try { setTelemetry(JSON.parse(event.data)); } catch (e) { }
    };
    return () => ws.close();
  }, []);

  return (
    <motion.div 
      className="min-h-screen flex flex-col font-sans bg-[#050505]"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }}
    >
      <header className="glass-header h-16 flex items-center justify-between px-6 lg:px-8 sticky top-0 z-40 border-b border-white/5">
        <div className="flex items-center space-x-4">
          <div className="w-8 h-8 rounded-full overflow-hidden border border-white/20">
             <Image src="/logo.jpeg" alt="Logo" width={32} height={32} className="object-cover" />
          </div>
          <div className="h-4 w-px bg-white/10 hidden sm:block"></div>
          <h1 className="text-lg font-bold tracking-wide uppercase hidden sm:block text-white">
            Drill <span className="text-blue-500 font-normal">Command</span>
          </h1>
        </div>
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-3 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            <span className="text-xs font-semibold text-green-400 tracking-wider">SQUAD ONLINE</span>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-20 lg:w-64 glass-panel border-y-0 border-l-0 hidden md:flex flex-col py-6">
          <nav className="space-y-1 px-3 flex-1">
            <NavItem icon={<LayoutGrid />} label="Dashboard" active />
            <NavItem icon={<Camera />} label="Multi-Cam Matrix" />
            <NavItem icon={<Users />} label="Squad Analysis" />
            <NavItem icon={<Activity />} label="Metrics Log" />
          </nav>
        </aside>

        {/* Content */}
        <main className="flex-1 p-4 lg:p-6 overflow-y-auto">
          <div className="max-w-[1800px] mx-auto space-y-6">
            
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
              <div>
                <h2 className="text-3xl font-bold tracking-tight text-white">Active Drill Session</h2>
                <p className="text-slate-400 mt-1 flex items-center space-x-2">
                  <span>Multi-Camera Tracking</span>
                  <ChevronRight className="w-4 h-4 text-slate-600" />
                  <span className="text-blue-400 font-bold uppercase tracking-wider">Mode: {currentMode}</span>
                </p>
              </div>
              <button className="px-6 py-2.5 rounded-lg bg-red-600/20 hover:bg-red-600/40 text-red-400 border border-red-500/30 font-medium text-sm transition-all">
                End Session
              </button>
            </div>

            {/* Top Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <StatCard title="Overall Alignment Score" value={`${telemetry.overall_score}%`} color="blue" subtitle="Aggregated multi-angle evaluation" />
              <div className="glass-panel rounded-2xl p-5 relative overflow-hidden flex items-center border-l-4 border-l-indigo-500">
                 <div className="flex-1">
                   <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-1">Squad Status</h3>
                   <div className={`text-3xl font-bold ${telemetry.status === 'Excellent' ? 'text-green-400' : telemetry.status === 'Good' ? 'text-yellow-400' : 'text-red-400'}`}>
                     {telemetry.status}
                   </div>
                 </div>
              </div>
              <StatCard title="Active Feeds" value="4/4" color="emerald" subtitle="Front, Top, Side, Feet" />
            </div>

            {/* Video Matrix & Telemetry */}
            <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
              
              {/* Multi-Camera Matrix (Spans 3 cols) */}
              <div className="xl:col-span-3">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {/* CAM 1: FRONT */}
                  <div className="glass-panel rounded-xl overflow-hidden p-1 relative">
                    <div className="absolute top-4 left-4 bg-black/70 backdrop-blur-md px-3 py-1.5 rounded-lg text-[10px] font-bold text-white z-10 flex items-center space-x-2 border border-white/10">
                      <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                      <span className="tracking-widest">CAM 1 - FRONT ANGLE</span>
                    </div>
                    <div className="aspect-video bg-[#0a0a0c] rounded-lg overflow-hidden border border-white/5 relative">
                      <img src="http://localhost:8000/api/video_feed/0" alt="Feed 1" className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                      <div className="absolute inset-0 flex items-center justify-center -z-10 text-slate-800 font-mono text-sm">NO SIGNAL</div>
                    </div>
                  </div>

                  {/* CAM 2: SIDE */}
                  <div className="glass-panel rounded-xl overflow-hidden p-1 relative">
                    <div className="absolute top-4 left-4 bg-black/70 backdrop-blur-md px-3 py-1.5 rounded-lg text-[10px] font-bold text-white z-10 tracking-widest border border-white/10">
                      CAM 2 - SIDE ANGLE
                    </div>
                    <div className="aspect-video bg-[#0a0a0c] rounded-lg overflow-hidden border border-white/5 relative">
                      <img src="http://localhost:8000/api/video_feed/1" alt="Feed 2" className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                      <div className="absolute inset-0 flex items-center justify-center -z-10 text-slate-800 font-mono text-sm">NO SIGNAL</div>
                    </div>
                  </div>

                  {/* CAM 3: TOP */}
                  <div className="glass-panel rounded-xl overflow-hidden p-1 relative">
                    <div className="absolute top-4 left-4 bg-black/70 backdrop-blur-md px-3 py-1.5 rounded-lg text-[10px] font-bold text-white z-10 tracking-widest border border-white/10">
                      CAM 3 - TOP ANGLE
                    </div>
                    <div className="aspect-video bg-[#0a0a0c] rounded-lg overflow-hidden border border-white/5 relative">
                      <img src="http://localhost:8000/api/video_feed/2" alt="Feed 3" className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                      <div className="absolute inset-0 flex items-center justify-center -z-10 text-slate-800 font-mono text-sm">NO SIGNAL</div>
                    </div>
                  </div>

                  {/* CAM 4: FEET */}
                  <div className="glass-panel rounded-xl overflow-hidden p-1 relative">
                    <div className="absolute top-4 left-4 bg-black/70 backdrop-blur-md px-3 py-1.5 rounded-lg text-[10px] font-bold text-white z-10 tracking-widest border border-white/10">
                      CAM 4 - FEET ANGLE
                    </div>
                    <div className="aspect-video bg-[#0a0a0c] rounded-lg overflow-hidden border border-white/5 relative">
                      <img src="http://localhost:8000/api/video_feed/3" alt="Feed 4" className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                      <div className="absolute inset-0 flex items-center justify-center -z-10 text-slate-800 font-mono text-sm">NO SIGNAL</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Telemetry Sidebar */}
              <div className="xl:col-span-1">
                <div className="glass-panel rounded-2xl p-6 h-full flex flex-col">
                  <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-white/5">
                    <Activity className="w-5 h-5 text-blue-400" />
                    <h2 className="text-lg font-semibold tracking-wide text-white">Live Telemetry</h2>
                  </div>
                  <div className="flex-1 flex flex-col space-y-5">
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
    <a href="#" className={`flex items-center space-x-3 px-3 lg:px-4 py-3 rounded-xl transition-all group ${active ? 'bg-blue-600/10 text-blue-400 relative' : 'text-slate-400 hover:text-white hover:bg-white/5'} ${danger ? 'mt-auto text-red-400 hover:bg-red-500/10' : ''}`}>
      {active && <motion.div layoutId="nav-indicator" className="absolute left-0 top-2 bottom-2 w-1 bg-blue-500 rounded-r-full" />}
      <div className={`w-5 h-5 ${active ? 'text-blue-400' : 'text-slate-500 group-hover:text-slate-300'}`}>{icon}</div>
      <span className="font-medium text-sm hidden lg:block tracking-wide">{label}</span>
    </a>
  );
}

function StatCard({ title, value, subtitle, color }: any) {
  const colorMap: Record<string, string> = { blue: "border-l-blue-500", emerald: "border-l-emerald-500" };
  return (
    <div className={`glass-panel rounded-2xl p-5 border-l-4 ${colorMap[color]} relative overflow-hidden group`}>
      <div className={`absolute -right-4 -top-4 w-24 h-24 bg-${color}-500/5 rounded-full blur-2xl group-hover:bg-${color}-500/10 transition-colors`}></div>
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-1">{title}</h3>
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      <p className="text-xs text-slate-500">{subtitle}</p>
    </div>
  );
}

function TelemetryGaugeCard({ label, value }: { label: string, value: number }) {
  return (
    <div className="bg-black/30 rounded-xl border border-white/5 p-4 flex flex-col justify-center hover:border-white/10 transition-colors">
      <div className="flex justify-between items-end mb-3">
        <h4 className="text-sm font-medium text-slate-300 tracking-wide">{label}</h4>
        <span className="text-xl font-bold text-white font-mono">{value}<span className="text-xs text-slate-500 ml-0.5">%</span></span>
      </div>
      <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
        <motion.div 
          className={`h-full rounded-full ${value >= 80 ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : value >= 50 ? 'bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.6)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]'}`}
          initial={{ width: 0 }} animate={{ width: `${value}%` }} transition={{ duration: 0.5 }}
        />
      </div>
    </div>
  );
}

// ==========================================
// APP ENTRY POINT
// ==========================================
export default function App() {
  const [appState, setAppState] = useState<"launch" | "onboarding" | "config" | "dashboard">("launch");
  const [workflow, setWorkflow] = useState<string[]>([]);

  return (
    <AnimatePresence mode="wait">
      {appState === "launch" && (
        <LaunchScreen key="launch" onComplete={() => setAppState("onboarding")} />
      )}
      {appState === "onboarding" && (
        <OnboardingScreen key="onboard" onNext={() => setAppState("config")} />
      )}
      {appState === "config" && (
        <ConfigScreen key="config" onStart={(wf) => { setWorkflow(wf); setAppState("dashboard"); }} />
      )}
      {appState === "dashboard" && (
        <Dashboard key="dashboard" activeWorkflow={workflow} />
      )}
    </AnimatePresence>
  );
}
