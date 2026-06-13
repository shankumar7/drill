"use client";

import React, { useEffect, useState, useRef } from "react";
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

  useEffect(() => {
    const bootSequence = [
      "Initializing core neural matrix...",
      "Loading pose estimation models...",
      "Calibrating multi-camera telemetry...",
      "Establishing secure WebSocket streams...",
      "System Ready."
    ];
    let step = 0;
    const interval = setInterval(() => {
      setProgress((prev) => {
        const next = prev + (100 / bootSequence.length);
        if (next >= 100) clearInterval(interval);
        return next;
      });
      setLogs((prev) => [...prev, bootSequence[step]]);
      step++;
      if (step >= bootSequence.length) setTimeout(onComplete, 1200);
    }, 600);
    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <motion.div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-white overflow-hidden font-sans"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, scale: 1.05 }} transition={{ duration: 0.8 }}
    >
      <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
        <div className="w-[800px] h-[800px] bg-blue-50/50 rounded-full blur-[100px]"></div>
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center w-full max-w-lg">
        {/* Geometric Loader */}
        <div className="relative w-48 h-48 mb-12 flex items-center justify-center">
          <motion.div 
            animate={{ rotate: 360 }} transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 border-[1px] border-dashed border-blue-300 rounded-full opacity-50"
          />
          <motion.div 
            animate={{ rotate: -360 }} transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
            className="absolute inset-4 border-[1px] border-blue-400 rounded-full opacity-30 border-t-transparent"
          />
          <motion.div 
            animate={{ scale: [0.95, 1.05, 0.95] }} transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            className="w-20 h-20 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-full shadow-[0_0_40px_rgba(59,130,246,0.4)] flex items-center justify-center"
          >
             <Shield className="w-8 h-8 text-white" />
          </motion.div>
        </div>

        {/* Typography */}
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3, duration: 0.8 }} className="text-center mb-8">
          <h1 className="text-4xl font-black tracking-widest text-slate-900 uppercase mb-2">Drill Command</h1>
          <p className="text-sm font-bold tracking-widest text-blue-500 uppercase">Analysis System</p>
        </motion.div>

        {/* Minimal Progress */}
        <div className="w-64 space-y-4">
          <div className="h-[2px] w-full bg-slate-200 rounded-full overflow-hidden relative">
            <motion.div
              className="absolute top-0 left-0 h-full bg-blue-500"
              initial={{ width: 0 }} animate={{ width: `${progress}%` }}
              transition={{ ease: "linear", duration: 0.1 }}
            />
          </div>
          <div className="h-6 flex items-center justify-center overflow-hidden">
             <AnimatePresence mode="wait">
               {logs.length > 0 && (
                 <motion.div
                   key={logs.length}
                   initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: -10, opacity: 0 }}
                   className="text-[10px] font-bold tracking-widest text-slate-400 uppercase text-center"
                 >
                   {logs[logs.length - 1]}
                 </motion.div>
               )}
             </AnimatePresence>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// ==========================================
function OnboardingScreen({ onNext }: { onNext: () => void }) {
  return (
    <motion.div
      className="fixed inset-0 z-40 flex items-center justify-center bg-slate-50 overflow-hidden"
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
      <div className="absolute top-8 left-8 w-16 h-16 border-t-2 border-l-2 border-blue-200 opacity-50"></div>
      <div className="absolute bottom-8 right-8 w-16 h-16 border-b-2 border-r-2 border-emerald-500/50 opacity-50"></div>

      <div className="bg-white shadow-lg border border-slate-200 p-12 lg:p-16 rounded-3xl max-w-5xl w-full mx-6 relative z-10 border border-slate-200 shadow-2xl bg-white">
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3, duration: 1, ease: "easeOut" }}>

          <div className="flex items-center space-x-4 mb-6">
            <Shield className="w-8 h-8 text-blue-500 opacity-80" />
            <h3 className="text-sm font-bold text-slate-500 tracking-[0.3em] uppercase">
              Simulation Development Division (SDD), MCEME
            </h3>
          </div>

          <h1 className="text-5xl lg:text-[5rem] font-black text-slate-900 tracking-tight mb-8 leading-[1.1]">
            Military Drill <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-cyan-500 to-emerald-500 drop-shadow-[0_0_15px_rgba(56,189,248,0.3)]">
              Analysis System.
            </span>
          </h1>

          <div className="flex items-center space-x-4 mb-10">
            <div className="w-32 h-1 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full"></div>
            <div className="w-4 h-1 bg-emerald-500 rounded-full"></div>
            <div className="w-2 h-1 bg-emerald-500 rounded-full opacity-50"></div>
          </div>

          <p className="text-lg lg:text-xl text-slate-400 max-w-3xl leading-relaxed mb-14 font-medium">
            A professional evaluation suite designed for rigorous posture and alignment tracking.
            Initialize the workspace to begin real-time, multi-camera drill compliance assessment powered by state-of-the-art neural engines.
          </p>

          <div className="flex items-center space-x-8">
            <button
              onClick={onNext}
              className="group relative overflow-hidden flex items-center justify-center space-x-4 bg-blue-600 text-white px-10 py-5 rounded-full font-bold text-lg hover:scale-[1.02] active:scale-95 transition-all shadow-[0_0_30px_rgba(255,255,255,0.15)] hover:shadow-[0_0_40px_rgba(255,255,255,0.3)]"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-blue-500 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
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
// 3. CONFIGURATION SCREEN (Redesigned)
// ==========================================
function ConfigScreen({ onStart }: { onStart: (workflow: string[]) => void }) {
  const [workflow, setWorkflow] = useState<string[]>([]);

  const categorizedActions = [
    {
      category: "STATIC POSTURES",
      actions: [
        { name: "Savdhan", desc: "Attention posture" },
        { name: "Vishram", desc: "Stand at ease" },
        { name: "Aaram Se", desc: "Relax" },
      ]
    },
    {
      category: "TURNS AT HALT",
      actions: [
        { name: "Dahine Murh", desc: "90° right turn" },
        { name: "Bayen Murh", desc: "90° left turn" },
        { name: "Pichhe Murh", desc: "180° about turn" },
      ]
    },
    {
      category: "MARCHING",
      actions: [
        { name: "Tej Chal", desc: "Quick march" },
        { name: "Dhire Chal", desc: "Slow march" },
        { name: "Tham", desc: "Halt" },
      ]
    },
    {
      category: "FORMATIONS",
      actions: [
        { name: "Khuli Line Chal", desc: "Open order" },
        { name: "Nikat Line Chal", desc: "Close order" },
        { name: "Saj", desc: "Dressing" },
        { name: "Kadwar Banana", desc: "Sizing squad" },
      ]
    },
    {
      category: "SALUTING",
      actions: [
        { name: "Samne Salute", desc: "Front salute" },
        { name: "Dahine Salute", desc: "Right salute" },
        { name: "Bayen Salute", desc: "Left salute" },
      ]
    },
    {
      category: "DISPERSAL",
      actions: [
        { name: "Line Tod", desc: "Fall out" },
        { name: "Visharjan", desc: "Dismiss" }
      ]
    }
  ];

  const handleAdd = (action: string) => {
    setWorkflow([...workflow, action]);
  };

  const handleRemove = (index: number) => {
    setWorkflow(workflow.filter((_, i) => i !== index));
  };

  return (
    <motion.div
      className="fixed inset-0 z-30 flex items-center justify-center bg-slate-50 overflow-hidden font-sans"
      initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      {/* Background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-blue-600/10 rounded-full blur-[120px] transform translate-x-1/3 -translate-y-1/3"></div>
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-emerald-600/10 rounded-full blur-[120px] transform -translate-x-1/3 translate-y-1/3"></div>
        <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, backgroundSize: '40px 40px' }}></div>
      </div>

      <div className="relative z-10 w-full h-full max-w-[1400px] mx-auto flex flex-col p-6 lg:p-10">

        {/* Header */}
        <div className="mb-6 flex justify-between items-end">
          <div>
            <h2 className="text-4xl font-black text-slate-900 tracking-tight uppercase drop-shadow-md">
              Configure Sequence
            </h2>
            <p className="text-slate-500 text-sm mt-1">Select drill actions from the database to build the evaluation timeline.</p>
          </div>
          <div className="text-right hidden sm:block">
            <div className="text-xs font-mono text-emerald-600 font-bold uppercase tracking-widest flex items-center justify-end space-x-2">
              <span className="w-1.5 h-1.5 bg-emerald-500 animate-pulse rounded-full shadow-sm"></span>
              <span>System Online</span>
            </div>
            <div className="text-slate-500 text-xs font-mono mt-1">TOTAL ACTIONS: {workflow.length}</div>
          </div>
        </div>

        {/* Two-pane layout: Selection (Left/Top) and Timeline (Right/Bottom) */}
        <div className="flex-1 flex flex-col lg:flex-row gap-6 min-h-0">

          {/* Action Categories (Scrollable) */}
          <div className="flex-1 overflow-y-auto custom-scrollbar pr-4 space-y-8 pb-10">
            {categorizedActions.map((cat, i) => (
              <div key={i} className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="h-[1px] flex-1 bg-white/5"></div>
                  <h3 className="text-xs font-bold tracking-[0.3em] text-slate-500 uppercase">{cat.category}</h3>
                  <div className="h-[1px] flex-1 bg-white/5"></div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {cat.actions.map((action) => (
                    <motion.div
                      key={action.name}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleAdd(action.name)}
                      className="bg-white shadow-lg border border-slate-200 p-4 rounded-xl cursor-pointer border border-slate-200 hover:border-blue-300 hover:bg-blue-50/50 transition-all shadow-md group relative overflow-hidden flex flex-col justify-center min-h-[80px]"
                    >
                      <div className="absolute -right-10 -top-10 w-24 h-24 bg-blue-500/5 rounded-full blur-2xl group-hover:bg-blue-500/10 transition-colors"></div>
                      <div className="flex justify-between items-start mb-1">
                        <h4 className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors leading-tight">{action.name}</h4>
                        <div className="w-5 h-5 shrink-0 rounded-full bg-slate-100 flex items-center justify-center group-hover:bg-blue-100 text-slate-400 group-hover:text-blue-600 transition-colors">
                          <Plus className="w-3 h-3" />
                        </div>
                      </div>
                      <p className="text-[10px] text-slate-500 leading-tight uppercase font-mono">{action.desc}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Timeline & Controls */}
          <div className="lg:w-[400px] xl:w-[450px] shrink-0 flex flex-col gap-4 h-[300px] lg:h-auto">
            <div className="flex-1 bg-white shadow-lg border border-slate-200 rounded-2xl p-6 border border-slate-200 flex flex-col relative overflow-hidden shadow-xl">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-600 to-emerald-400"></div>

              <h3 className="text-xs font-bold tracking-[0.2em] text-slate-900 uppercase mb-4 flex items-center">
                <Activity className="w-4 h-4 mr-2 text-blue-600" />
                Active Sequence
              </h3>

              <div className="flex-1 bg-slate-50 rounded-xl border border-slate-200 p-4 overflow-y-auto custom-scrollbar relative">
                {workflow.length === 0 ? (
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500 font-mono tracking-widest text-xs font-semibold">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-pulse mb-3"></span>
                    AWAITING INPUT
                  </div>
                ) : (
                  <div className="flex flex-col space-y-2">
                    <AnimatePresence>
                      {workflow.map((action, idx) => (
                        <motion.div
                          key={`${action}-${idx}`}
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, scale: 0.9, x: -20 }}
                          onClick={() => handleRemove(idx)}
                          className="group cursor-pointer bg-gradient-to-r from-blue-50 to-transparent border-l-2 border-blue-500 px-4 py-3 rounded flex items-center justify-between hover:bg-red-50 hover:border-red-500 transition-colors"
                        >
                          <div className="flex items-center space-x-3">
                            <span className="text-blue-600 font-mono font-bold text-xs">{(idx + 1).toString().padStart(2, '0')}</span>
                            <span className="text-slate-800 font-semibold text-sm group-hover:text-red-600">{action}</span>
                          </div>
                          <div className="w-5 h-5 bg-red-100 rounded flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                            <span className="text-red-600 font-bold text-[10px]">✕</span>
                          </div>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                )}
              </div>
            </div>

            {/* Start Button */}
            <button
              onClick={() => onStart(workflow)}
              disabled={workflow.length === 0}
              className={`w-full py-5 rounded-2xl font-bold text-sm tracking-widest uppercase transition-all flex items-center justify-center space-x-3 shadow-lg
                ${workflow.length > 0
                  ? 'bg-emerald-600 hover:bg-emerald-500 text-slate-900 shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:scale-[1.02] active:scale-95'
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-300'}`}
            >
              <span>Initialize Evaluation</span>
              <ChevronRightCircle className={`w-5 h-5 ${workflow.length > 0 ? 'text-slate-900' : 'text-slate-400'}`} />
            </button>
          </div>
        </div>

      </div>
    </motion.div>
  );
}

// ==========================================
// 4. COUNTDOWN SCREEN
// ==========================================
function CountdownScreen({ onComplete }: { onComplete: () => void }) {
  const [count, setCount] = useState(5);

  useEffect(() => {
    if (count > 0) {
      const timer = setTimeout(() => setCount(count - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      const timer = setTimeout(onComplete, 800);
      return () => clearTimeout(timer);
    }
  }, [count, onComplete]);

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-50"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
    >
      <div className="absolute inset-0 pointer-events-none z-0 flex items-center justify-center">
        <div className="absolute inset-0 opacity-[0.04]" style={{ backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, backgroundSize: '30px 30px' }}></div>
        <div className="w-[600px] h-[600px] bg-emerald-600/10 rounded-full blur-[150px]"></div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={count}
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 1.5, opacity: 0 }}
          transition={{ duration: 0.5 }}
          className="text-[12rem] font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-slate-800 to-slate-500 drop-shadow-[0_0_30px_rgba(0,0,0,0.1)] relative z-10"
        >
          {count > 0 ? count : "GO"}
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
}

// ==========================================
// 5. MAIN DASHBOARD (Multi-Camera)
// ==========================================
import { globalCadetTracker } from "@/utils/CadetTracker";
// Duplicate import removed
function Dashboard({ activeWorkflow, onComplete }: { activeWorkflow: string[], onComplete: (results: any[]) => void }) {
  const [selectedCadet, setSelectedCadet] = useState<string | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [sessionResults, setSessionResults] = useState<{ drill: string, pass: boolean, score: number }[]>([]);
  const [wsStatus, setWsStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");
  const [showEvaluationModal, setShowEvaluationModal] = useState(false);
  
  const [telemetry, setTelemetry] = useState<{ metrics: Record<string, any>, overall_score: number, status: string, detected_ids: number[] }>({
    metrics: {},
    overall_score: 0,
    status: "Initializing...",
    detected_ids: []
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const connectWebSocket = () => {
    const ws = new WebSocket("ws://localhost:8000/ws/telemetry");
    wsRef.current = ws;

    ws.onopen = () => {
      setWsStatus("connected");
      console.log("Telemetry Connected");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const { overall_score, status, detected_ids, ...metrics } = data;
        
        const cleanMetrics: Record<string, any> = {};
        for (const key in metrics) {
           if (metrics[key] && metrics[key].status !== "not_evaluable") {
               const formattedKey = key.split('_').map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
               cleanMetrics[formattedKey] = metrics[key];
           }
        }
        
        setTelemetry({
          metrics: cleanMetrics,
          overall_score: overall_score || 0,
          status: status || "Initializing...",
          detected_ids: detected_ids || []
        });
      } catch (e) {
        console.warn("WebSocket parse error", e);
      }
    };

    ws.onclose = () => {
      setWsStatus("disconnected");
      reconnectTimeout.current = setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = () => ws.close();
  };

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (reconnectTimeout.current) {
  clearTimeout(reconnectTimeout.current);
}
      wsRef.current?.close();
    };
  }, []);

  const rawMode = activeWorkflow.length > 0 ? activeWorkflow[currentStepIndex].toUpperCase() : "SAVDHAN";
  const modeMap: Record<string, string> = {
    "SAMNE SALUTE": "FRONT_SALUTE",
    "BAYEN SALUTE": "BAYE_SALUTE",
    "DAHINE SALUTE": "DAINE_SALUTE"
  };
  const currentMode = modeMap[rawMode] || rawMode;

  useEffect(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ mode: currentMode }));
    }
  }, [currentMode]);

  const [availableIds, setAvailableIds] = useState<number[]>([1, 2, 3]);

  const lockCadet = async (id: number) => {
    setSelectedCadet(id.toString());
    try {
      await fetch("http://localhost:8000/api/lock_cadet", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({track_id: id})
      });
    } catch(e) { console.error(e); }
  };

  const handleNextDrill = () => {
    const finalScore = telemetry.overall_score;
    const isPass = finalScore >= 80;
    
    const newResults = [...sessionResults, {
      drill: activeWorkflow[currentStepIndex],
      pass: isPass,
      score: finalScore
    }];
    
    setSessionResults(newResults);

    if (currentStepIndex < activeWorkflow.length - 1) {
      setCurrentStepIndex(currentStepIndex + 1);
      setTelemetry({ metrics: {}, overall_score: 0, status: "Initializing...", detected_ids: [] });
    } else {
      onComplete(newResults);
    }
  };

  return (
    <motion.div
      className="min-h-screen flex flex-col font-sans bg-slate-50 relative"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }}
    >
      <header className="bg-white shadow-sm h-16 flex items-center justify-between px-6 lg:px-8 sticky top-0 z-40 border-b border-white/5">
        <div className="flex items-center space-x-4">
          <div className="w-8 h-8 rounded-full overflow-hidden border border-white/20">
            <Image src="/logo.jpeg" alt="Logo" width={32} height={32} className="object-cover" />
          </div>
          <div className="h-4 w-px bg-white/10 hidden sm:block"></div>
          <h1 className="text-lg font-bold tracking-wide uppercase hidden sm:block text-slate-800">
            Drill <span className="text-blue-500 font-normal">Command</span>
          </h1>
        </div>
        
        </header>

      <div className="flex flex-1 overflow-hidden">
        

        {/* Content */}
        <main className="flex-1 p-4 lg:p-6 overflow-y-auto">
          <div className="max-w-[1800px] mx-auto space-y-6">

            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
              <div>
                <h2 className="text-3xl font-extrabold tracking-tight text-slate-900">Active Drill Session</h2>
                <p className="text-slate-500 mt-1 flex items-center space-x-2">
                  <span>Sequence:</span>
                  <ChevronRight className="w-4 h-4 text-slate-400" />
                  <span className="text-blue-600 font-bold uppercase tracking-wider">
                    {activeWorkflow[currentStepIndex] || "SAVDHAN"}
                  </span>
                  <span className="text-slate-400 font-mono text-xs ml-2">
                    ({currentStepIndex + 1} / {activeWorkflow.length || 1})
                  </span>
                </p>
              </div>
              
            </div>

                        {/* Massive Evaluation Badge */}
            <div className={`w-full rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-between border shadow-xl relative overflow-hidden transition-all mb-6
              ${telemetry.status === 'Excellent' || telemetry.status === 'Good' 
                ? 'bg-emerald-50 border-emerald-200' 
                : 'bg-red-50 border-red-200'}`}>
              
              <div className={`absolute -right-20 -top-20 w-64 h-64 rounded-full blur-[80px] opacity-50
                ${telemetry.status === 'Excellent' || telemetry.status === 'Good' ? 'bg-emerald-400' : 'bg-red-400'}`} />

              <div className="flex items-center space-x-6 relative z-10 mb-4 md:mb-0">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center shadow-inner
                  ${telemetry.status === 'Excellent' || telemetry.status === 'Good' ? 'bg-emerald-100 text-emerald-600' : 'bg-red-100 text-red-600'}`}>
                  {telemetry.status === 'Excellent' || telemetry.status === 'Good' ? <CheckCircle className="w-8 h-8" /> : <XCircle className="w-8 h-8" />}
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-500 tracking-widest uppercase mb-1">Live Evaluation Status</h3>
                  <div className={`text-4xl md:text-5xl font-black uppercase tracking-tight
                    ${telemetry.status === 'Excellent' || telemetry.status === 'Good' ? 'text-emerald-700' : 'text-red-700'}`}>
                    {telemetry.status === "Initializing..." ? "WAITING..." : (telemetry.status === 'Excellent' || telemetry.status === 'Good' ? 'PASS' : 'FAIL')}
                  </div>
                </div>
              </div>

              <button onClick={() => setShowEvaluationModal(true)} 
                className="relative z-10 px-8 py-4 bg-white hover:bg-slate-50 text-slate-900 font-bold text-sm tracking-widest uppercase rounded-xl border border-slate-200 shadow-md transition-transform hover:scale-[1.02] active:scale-95 flex items-center space-x-3">
                <Activity className="w-5 h-5 text-blue-500" />
                <span>View Pass/Fail Reason</span>
              </button>
            </div>

                                    {/* Video Matrix & Telemetry */}
            <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">

              {/* Multi-Camera Matrix (Spans 3 cols) */}
              <div className="xl:col-span-4 flex flex-col gap-6">

                {/* Main Camera (Front) - Huge */}
                <div className="bg-white shadow-lg border border-slate-200 overflow-hidden p-1 relative group w-full aspect-video border border-blue-200 rounded-xl">
                  <div className="absolute inset-1 pointer-events-none z-20 border border-white/5 rounded-xl">
                    <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md px-4 py-2 rounded-lg text-xs font-bold text-slate-900 flex items-center space-x-2 border border-white/10 shadow-lg">
                      <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse shadow-[0_0_8px_rgba(239,68,68,1)]"></span>
                      <span className="tracking-widest uppercase">MAIN CAMERA (FRONT)</span>
                    </div>
                  </div>

                  <div className="w-full h-full bg-slate-200 rounded-xl overflow-hidden relative z-10 flex items-center justify-center">
                    {selectedCadet ? (
                      <img 
                        src="http://localhost:8000/api/video_feed/0" 
                        alt="Main Camera Feed" 
                        className="w-full h-full object-cover transition-opacity duration-300"
                        onError={(e) => { e.currentTarget.style.display = 'none'; }}
                      />
                    ) : (
                      <>
                        <img 
                          src="http://localhost:8000/api/video_feed/0" 
                          alt="Main Camera Feed (Unselected)" 
                          className="w-full h-full object-cover transition-opacity duration-300 opacity-50"
                          onError={(e) => { e.currentTarget.style.display = 'none'; }}
                        />
                        <div 
                          className="absolute inset-0 z-30 flex flex-col items-center justify-end pb-8 bg-gradient-to-t from-black/80 via-transparent to-transparent transition-colors pointer-events-none"
                        >
                          <div className="pointer-events-auto flex flex-col items-center">
                            <h3 className="text-xl font-bold text-white mb-2 drop-shadow-md">AWAITING TARGET LOCK</h3>
                            <p className="text-sm text-slate-300 mb-4 drop-shadow text-center">Observe the camera feed and select a cadet ID</p>
                            <div className="flex flex-wrap justify-center gap-2 max-w-lg px-4">
                              {telemetry.detected_ids && telemetry.detected_ids.length > 0 ? (
                                telemetry.detected_ids.map(id => (
                                  <button
                                    key={id}
                                    onClick={() => lockCadet(id)}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg font-bold text-sm tracking-wider hover:bg-blue-500 transition-colors shadow-lg shadow-blue-900/50 border border-blue-400/30 flex items-center space-x-2"
                                  >
                                    <Users className="w-4 h-4 text-emerald-400" />
                                    <span>TARGET ID: {id}</span>
                                  </button>
                                ))
                              ) : (
                                <div className="px-6 py-2 bg-slate-900/60 backdrop-blur-md rounded-full text-slate-400 font-mono text-xs border border-white/10 uppercase tracking-widest shadow-lg">
                                  WAITING FOR CADETS TO APPEAR IN FRAME...
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                {/* Secondary Cameras Grid (Side and Back) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {[
                    { id: 1, label: "EXTERNAL CAMERA (SIDE)" },
                    { id: 2, label: "EXTERNAL CAMERA (BACK)" }
                  ].map((cam) => (
                    <div key={cam.id} className="bg-white shadow-lg border border-slate-200 rounded-2xl overflow-hidden p-1 relative group bg-slate-50 aspect-video">
                      <div className="absolute inset-1 pointer-events-none z-20 border border-white/5 rounded-xl">
                        <div className="absolute top-3 left-3 bg-black/60 backdrop-blur-md px-2 py-1 rounded text-[9px] font-bold text-slate-700 flex items-center space-x-1 border border-white/10">
                          <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
                          <span className="tracking-widest uppercase">{cam.label}</span>
                        </div>
                      </div>

                      <div className="w-full h-full bg-slate-200 rounded-xl overflow-hidden relative z-10 flex items-center justify-center">
                        <img 
                          src={`http://localhost:8000/api/video_feed/${cam.id}`} 
                          alt={`Aux Camera ${cam.id}`} 
                          className="w-full h-full object-cover transition-opacity duration-300"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            e.currentTarget.nextElementSibling?.classList.remove('hidden');
                            e.currentTarget.nextElementSibling?.classList.add('flex');
                          }}
                        />
                        <div className="hidden flex-col items-center justify-center opacity-30 absolute inset-0">
                          <Activity className="w-8 h-8 text-slate-500 mb-2" />
                          <span className="text-xs font-bold text-slate-500 tracking-widest">NO SIGNAL</span>
                        </div>
                      </div>
                      <div className="absolute inset-0 flex flex-col items-center justify-center -z-10 bg-slate-200">
                          <Activity className="w-6 h-6 text-slate-700 mb-1 opacity-50" />
                        </div>
                    </div>
                  ))}
                </div>
              </div>

              
            </div>
          </div>
        </main>
      </div>

        {showEvaluationModal && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm" onClick={() => setShowEvaluationModal(false)}>
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-8 relative max-h-[80vh] flex flex-col border border-slate-200" onClick={e => e.stopPropagation()}>
               <div className="flex justify-between items-center mb-6 border-b border-slate-100 pb-4">
                 <h2 className="text-2xl font-bold text-slate-900">Drill Pass/Fail Reasons</h2>
                 <button onClick={() => setShowEvaluationModal(false)} className="text-slate-400 hover:text-slate-600 font-bold text-3xl leading-none">&times;</button>
               </div>
               <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-4">
                 {Object.entries(telemetry.metrics).map(([label, value]) => (
                    <TelemetryGaugeCard key={label} label={label} value={value} />
                 ))}
                 {Object.keys(telemetry.metrics).length === 0 && (
                    <div className="text-slate-500 text-sm italic text-center mt-10 font-medium">Waiting for cadet lock...</div>
                 )}
               </div>
            </div>
          </div>
        )}
    </motion.div>
  );
}

// ==========================================
// HELPER COMPONENTS
// ==========================================

function NavItem({ icon, label, active = false, danger = false }: any) {
  return (
    <a href="#" className={`flex items-center space-x-3 px-3 lg:px-4 py-3 rounded-xl transition-all group ${active ? 'bg-blue-600/10 text-blue-600 relative' : 'text-slate-500 hover:text-slate-900 hover:bg-white/5'} ${danger ? 'mt-auto text-red-400 hover:bg-red-500/10' : ''}`}>
      {active && <motion.div layoutId="nav-indicator" className="absolute left-0 top-2 bottom-2 w-1 bg-blue-500 rounded-r-full" />}
      <div className={`w-5 h-5 ${active ? 'text-blue-600' : 'text-slate-500 group-hover:text-slate-700'}`}>{icon}</div>
      <span className="font-medium text-sm hidden lg:block tracking-wide">{label}</span>
    </a>
  );
}

function StatCard({ title, value, subtitle, color }: any) {
  const colorMap: Record<string, string> = { blue: "border-l-blue-500", emerald: "border-l-emerald-500" };
  return (
    <div className={`bg-white shadow-lg border border-slate-200 rounded-2xl p-5 border-l-4 ${colorMap[color]} relative overflow-hidden group`}>
      <div className={`absolute -right-4 -top-4 w-24 h-24 bg-${color}-500/5 rounded-full blur-2xl group-hover:bg-${color}-500/10 transition-colors`} />
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-1">{title}</h3>
      <div className="text-3xl font-bold text-slate-900 mb-1">{value}</div>
      <p className="text-xs text-slate-500">{subtitle}</p>
    </div>
  );
}

import { CheckCircle, XCircle } from "lucide-react";
function TelemetryGaugeCard({ label, value }: { label: string; value: any }) {
  if (typeof value === "number") return null; // Fallback
  const isPass = value.status === "pass";
  return (
    <div className={`bg-white shadow-sm rounded-xl border ${isPass ? 'border-emerald-200 bg-emerald-50/30' : 'border-red-200 bg-red-50/30'} p-4 flex flex-col justify-center hover:shadow-md transition-all`}>
      <div className="flex justify-between items-center mb-2">
        <h4 className="text-sm font-semibold text-slate-800 tracking-wide">{label}</h4>
        {isPass ? <CheckCircle className="w-5 h-5 text-emerald-500" /> : <XCircle className="w-5 h-5 text-red-500" />}
      </div>
      <div className="text-xs text-slate-500 font-mono mt-1 leading-relaxed">
        {value.reason}
      </div>
    </div>
  );
}

// ==========================================
// RESULTS SCREEN
// ==========================================
function ResultsScreen({ results, onRestart }: { results: any[]; onRestart: () => void }) {
  const passed = results.filter(r => r.pass).length;
  const total = results.length;

  return (
    <motion.div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-slate-50 overflow-hidden" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,#010101_80%)]" />
        <div className="w-[800px] h-[800px] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-blue-600/10 rounded-full blur-[120px]" />
      </div>
      <div className="relative z-10 w-full max-w-4xl p-8 bg-white shadow-lg border border-slate-200 rounded-3xl border border-slate-200 shadow-2xl bg-white">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-black text-slate-900 uppercase tracking-wider mb-2">Final Evaluation</h1>
          <p className="text-slate-500">Sequence completed. Here is the strict rule‑based breakdown.</p>
        </div>
        <div className="grid grid-cols-3 gap-6 mb-10 text-center">
          <div className="p-6 bg-white/5 rounded-2xl border border-white/10">
            <div className="text-sm font-bold text-slate-500 tracking-widest uppercase mb-2">Total Drills</div>
            <div className="text-4xl font-black text-slate-900">{total}</div>
          </div>
          <div className="p-6 bg-white/5 rounded-2xl border border-white/10">
            <div className="text-sm font-bold text-slate-500 tracking-widest uppercase mb-2">Passed</div>
            <div className="text-4xl font-black text-emerald-400">{passed}</div>
          </div>
          <div className="p-6 bg-white/5 rounded-2xl border border-white/10">
            <div className="text-sm font-bold text-slate-500 tracking-widest uppercase mb-2">Failed</div>
            <div className="text-4xl font-black text-red-400">{total - passed}</div>
          </div>
        </div>
        <div className="space-y-3 mb-10 max-h-[40vh] overflow-y-auto custom-scrollbar pr-4">
          {results.map((r, i) => (
            <div key={i} className="flex items-center justify-between p-4 bg-white/5 border border-white/10 rounded-xl">
              <div className="flex items-center space-x-4">
                <span className="text-slate-500 font-mono font-bold text-sm">{(i + 1).toString().padStart(2, '0')}</span>
                <span className="text-slate-900 font-bold text-lg">{r.drill}</span>
              </div>
              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <div className="text-xs text-slate-500 uppercase tracking-widest">Score</div>
                  <div className="font-mono text-slate-900 font-bold">{r.score}%</div>
                </div>
                <div className={`px-4 py-1.5 rounded-md font-bold text-xs uppercase tracking-wider ${r.pass ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-red-100 text-red-400 border border-red-500/30'}`}>
                  {r.pass ? 'PASS' : 'FAIL'}
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="text-center">
          <button onClick={onRestart} className="px-10 py-4 bg-blue-600 text-white font-bold uppercase tracking-widest rounded-full hover:scale-105 transition-transform shadow-[0_0_30px_rgba(255,255,255,0.15)]">
            New Session
          </button>
        </div>
      </div>
    </motion.div>
  );
}

// ==========================================
// APP ENTRY POINT
// ==========================================
export default function App() {
  const [appState, setAppState] = useState<"launch" | "onboarding" | "config" | "countdown" | "dashboard" | "results">("launch");
  const [workflow, setWorkflow] = useState<string[]>([]);
  const [finalResults, setFinalResults] = useState<any[]>([]);

  return (
    <AnimatePresence mode="wait">
      {appState === "launch" && (
        <LaunchScreen key="launch" onComplete={() => setAppState("onboarding")} />
      )}
      {appState === "onboarding" && (
        <OnboardingScreen key="onboard" onNext={() => setAppState("config")} />
      )}
      {appState === "config" && (
        <ConfigScreen key="config" onStart={(wf) => { setWorkflow(wf); setAppState("countdown"); }} />
      )}
      {appState === "countdown" && (
        <CountdownScreen key="countdown" onComplete={() => setAppState("dashboard")} />
      )}
      {appState === "dashboard" && (
        <Dashboard key="dashboard" activeWorkflow={workflow} onComplete={(results) => { setFinalResults(results); setAppState("results"); }} />
      )}
      {appState === "results" && (
        <ResultsScreen key="results" results={finalResults} onRestart={() => setAppState("launch")} />
      )}
    </AnimatePresence>
  );
}
