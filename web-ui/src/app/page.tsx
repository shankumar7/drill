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

      <div className="relative z-10 w-full max-w-4xl px-4 flex flex-col items-center gap-8 mt-[-2vh]">

        {/* Cinematic Logo Container - MASSIVELY SCALED UP */}
        <div className="relative w-[500px] h-[500px] flex items-center justify-center mb-4">
          {/* Outer Pulsing Rings */}
          <motion.div
            className="absolute inset-[-40px] border-2 border-blue-500/20 rounded-full"
            animate={{ scale: [1, 1.3, 1], opacity: [0.1, 0, 0.1] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.div
            className="absolute inset-[-20px] border-2 border-emerald-400/20 rounded-full"
            animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0, 0.3] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
          />

          {/* Logo Container */}
          <motion.div
            className="w-[400px] h-[400px] bg-[#030305] rounded-full overflow-hidden border-[6px] border-white/5 shadow-[0_0_100px_rgba(59,130,246,0.5)] relative z-10"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          >
            <div className="absolute inset-0 bg-blue-500/10 mix-blend-overlay z-20 pointer-events-none"></div>

            <Image src="/logo.jpeg" alt="System Logo" fill className="object-cover opacity-100" />
          </motion.div>
        </div>

        {/* Typography & Boot Sequence */}
        <div className="w-full max-w-2xl flex flex-col items-center text-center">
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 1, delay: 0.4 }}
          >
            <h1 className="text-5xl md:text-6xl font-black tracking-tight text-white mb-2 leading-none uppercase drop-shadow-lg">
              Military Drill
            </h1>
            <h1 className="text-4xl md:text-5xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 mb-8 leading-none drop-shadow-md">
              Analysis System
            </h1>
          </motion.div>

          {/* Progress Bar Container */}
          <motion.div
            className="w-full space-y-3 mb-6"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1, delay: 0.7 }}
          >
            <div className="flex justify-between items-end px-1">
              <span className="text-xs font-mono text-blue-400 tracking-widest uppercase flex items-center space-x-2">
                <span className="w-1.5 h-1.5 bg-blue-500 animate-pulse rounded-full"></span>
                <span>Booting Neural Engine</span>
              </span>
              <span className="text-sm font-mono text-white font-bold">{Math.floor(progress)}%</span>
            </div>
            <div className="h-2 w-full bg-[#111] rounded overflow-hidden relative border border-white/10">
              <motion.div
                className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-600 to-emerald-400 shadow-[0_0_15px_rgba(56,189,248,0.8)]"
                initial={{ width: 0 }} animate={{ width: `${progress}%` }}
                transition={{ ease: "linear", duration: 0.1 }}
              />
              <motion.div
                className="absolute top-0 bottom-0 w-32 bg-white/30 skew-x-[-20deg]"
                animate={{ left: ['-100%', '200%'] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
              />
            </div>
          </motion.div>

          {/* Terminal Logs */}
          <div className="w-full h-24 bg-[#050508]/80 backdrop-blur-md border border-white/10 rounded-lg p-4 overflow-hidden shadow-inner relative text-left">
            <div className="absolute inset-0 bg-[linear-gradient(rgba(0,0,0,0)_50%,rgba(0,0,0,0.25)_50%)] bg-[length:100%_4px] pointer-events-none z-10"></div>
            <div className="flex flex-col space-y-1 relative z-0">
              {logs.map((log, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`text-[11px] font-mono tracking-wider ${index === logs.length - 1 ? 'text-emerald-400' : 'text-slate-400'}`}
                >
                  {`> ${log}`}
                </motion.div>
              ))}
              {progress < 100 && (
                <motion.div
                  animate={{ opacity: [1, 0] }} transition={{ repeat: Infinity, duration: 0.5 }}
                  className="text-[11px] font-mono text-emerald-400 mt-1"
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
            Military Drill <br />
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
      className="fixed inset-0 z-30 flex items-center justify-center bg-[#010101] overflow-hidden font-sans"
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
            <h2 className="text-4xl font-black text-white tracking-tight uppercase drop-shadow-md">
              Configure Sequence
            </h2>
            <p className="text-slate-400 text-sm mt-1">Select drill actions from the database to build the evaluation timeline.</p>
          </div>
          <div className="text-right hidden sm:block">
            <div className="text-xs font-mono text-emerald-400 uppercase tracking-widest flex items-center justify-end space-x-2">
              <span className="w-1.5 h-1.5 bg-emerald-500 animate-pulse rounded-full"></span>
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
                      className="glass-panel p-4 rounded-xl cursor-pointer border border-white/5 hover:border-blue-500/50 hover:bg-blue-900/10 transition-all shadow-md group relative overflow-hidden flex flex-col justify-center min-h-[80px]"
                    >
                      <div className="absolute -right-10 -top-10 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl group-hover:bg-blue-500/20 transition-colors"></div>
                      <div className="flex justify-between items-start mb-1">
                        <h4 className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors leading-tight">{action.name}</h4>
                        <div className="w-5 h-5 shrink-0 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-blue-500/20 text-slate-400 group-hover:text-blue-400 transition-colors">
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
            <div className="flex-1 glass-panel rounded-2xl p-6 border border-white/10 flex flex-col relative overflow-hidden shadow-2xl">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-600 to-emerald-400"></div>

              <h3 className="text-xs font-bold tracking-[0.2em] text-white uppercase mb-4 flex items-center">
                <Activity className="w-4 h-4 mr-2 text-blue-400" />
                Active Sequence
              </h3>

              <div className="flex-1 bg-[#050508]/80 rounded-xl border border-white/5 p-4 overflow-y-auto custom-scrollbar relative">
                {workflow.length === 0 ? (
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-600 font-mono tracking-widest text-xs">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-700 animate-pulse mb-3"></span>
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
                          className="group cursor-pointer bg-gradient-to-r from-blue-900/20 to-transparent border-l-2 border-blue-500 px-4 py-3 rounded flex items-center justify-between hover:bg-red-900/20 hover:border-red-500 transition-colors"
                        >
                          <div className="flex items-center space-x-3">
                            <span className="text-blue-500 font-mono font-bold text-xs opacity-70">{(idx + 1).toString().padStart(2, '0')}</span>
                            <span className="text-white font-semibold text-sm group-hover:text-red-200">{action}</span>
                          </div>
                          <div className="w-5 h-5 bg-red-500/20 rounded flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                            <span className="text-red-400 font-bold text-[10px]">✕</span>
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
                  ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:scale-[1.02] active:scale-95'
                  : 'bg-slate-800/50 text-slate-500 cursor-not-allowed border border-white/5'}`}
            >
              <span>Initialize Evaluation</span>
              <ChevronRightCircle className={`w-5 h-5 ${workflow.length > 0 ? 'text-white' : 'text-slate-600'}`} />
            </button>
          </div>
        </div>

      </div>
    </motion.div>
  );
}

// ==========================================
// 4. MAIN DASHBOARD (Multi-Camera)
// ==========================================
import { globalCadetTracker } from "@/utils/CadetTracker";
import { CameraFeed } from "@/components/CameraFeed";
import type { SavadhanTelemetry } from "@/components/PostureAnalyzer";

function Dashboard({ activeWorkflow }: { activeWorkflow: string[] }) {
  const [telemetry, setTelemetry] = useState({
    torso_posture: 0,
    heel_alignment: 0,
    foot_angle: 0,
    arm_alignment: 0,
    overall_score: 0,
    status: "Initializing...",
  });

  const [analyzer, setAnalyzer] = useState<any>(null);
  const [availableCameras, setAvailableCameras] = useState<MediaDeviceInfo[]>([]);
  
  useEffect(() => {
    // Dynamically load PostureAnalyzer
    import("@/components/PostureAnalyzer").then((mod) => {
      setAnalyzer(new mod.default([]));
    });

    // Enumerate cameras
    navigator.mediaDevices.enumerateDevices().then(devices => {
      setAvailableCameras(devices.filter(d => d.kind === 'videoinput'));
    }).catch(e => console.error("Could not enumerate cameras", e));
  }, []);

  const currentMode = activeWorkflow.length > 0 ? activeWorkflow[0].toUpperCase() : "SAVDHAN";

  const handleFrame = async (cameraId: string, frame: ImageData) => {
    if (!analyzer) return;
    try {
      const result: SavadhanTelemetry = await analyzer.predictFrame(frame);
      const cadetId = globalCadetTracker.getCadetId(cameraId, result.isPoseDetected);
      
      if (cadetId) {
        setTelemetry(prev => ({
          torso_posture: Math.round((prev.torso_posture + result.torso_posture) / 2),
          heel_alignment: Math.round((prev.heel_alignment + result.heel_alignment) / 2),
          foot_angle: Math.round((prev.foot_angle + result.foot_angle) / 2),
          arm_alignment: Math.round((prev.arm_alignment + result.arm_alignment) / 2),
          overall_score: Math.round((prev.overall_score + result.overall_score) / 2),
          status: result.overall_score > 80 ? "Excellent" : result.overall_score > 50 ? "Good" : "Needs Correction",
        }));
      }
    } catch (e) {
      console.warn("Pose estimation error", e);
    }
  };

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
                  <span>Sequence:</span>
                  <ChevronRight className="w-4 h-4 text-slate-600" />
                  <span className="text-blue-400 font-bold uppercase tracking-wider">
                    {activeWorkflow.join(" → ") || "SAVDHAN"}
                  </span>
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
              <div className="xl:col-span-3 flex flex-col gap-6">

                {/* Main Camera (Front) - Huge */}
                <div className="glass-panel rounded-2xl overflow-hidden p-1 relative group bg-[#020203] shadow-2xl h-[500px] border border-blue-500/20">
                  <div className="absolute inset-1 pointer-events-none z-20 border border-white/5 rounded-xl">
                    <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md px-4 py-2 rounded-lg text-xs font-bold text-white flex items-center space-x-2 border border-white/10 shadow-lg">
                      <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse shadow-[0_0_8px_rgba(239,68,68,1)]"></span>
                      <span className="tracking-widest uppercase">MAIN CAMERA (FRONT)</span>
                    </div>
                  </div>

                  <div className="w-full h-full bg-[#050508] rounded-xl overflow-hidden relative z-10 flex items-center justify-center">
                    <CameraFeed 
                      cadetId="CADET-01"
                      deviceId={availableCameras[0]?.deviceId}
                      className="w-full h-full object-contain transition-opacity duration-300"
                      onFrame={(frame) => handleFrame("cam-main", frame)}
                    />
                  </div>
                </div>

                {/* Secondary Cameras Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {[
                    { id: 1, label: "EXTERNAL CAMERA (SIDE)" },
                    { id: 2, label: "AUX FEED 1 (TOP)" },
                    { id: 3, label: "AUX FEED 2 (FEET)" }
                  ].map((cam) => (
                    <div key={cam.id} className="glass-panel rounded-2xl overflow-hidden p-1 relative group bg-[#020203] aspect-video">
                      <div className="absolute inset-1 pointer-events-none z-20 border border-white/5 rounded-xl">
                        <div className="absolute top-3 left-3 bg-black/60 backdrop-blur-md px-2 py-1 rounded text-[9px] font-bold text-slate-300 flex items-center space-x-1 border border-white/10">
                          <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
                          <span className="tracking-widest uppercase">{cam.label}</span>
                        </div>
                      </div>

                      <div className="w-full h-full bg-[#050508] rounded-xl overflow-hidden relative z-10 flex items-center justify-center">
                        {availableCameras.length > cam.id ? (
                          <CameraFeed 
                            cadetId="CADET-01"
                            deviceId={availableCameras[cam.id].deviceId}
                            className="w-full h-full object-cover transition-opacity duration-300"
                            onFrame={(frame) => handleFrame(`cam-aux-${cam.id}`, frame)}
                          />
                        ) : (
                          <div className="flex flex-col items-center justify-center opacity-30">
                            <Activity className="w-8 h-8 text-slate-500 mb-2" />
                            <span className="text-xs font-bold text-slate-500 tracking-widest">NO SIGNAL</span>
                          </div>
                        )}
                      </div>
                      <div className="absolute inset-0 flex flex-col items-center justify-center -z-10 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-900 to-[#050508]">
                          <Activity className="w-6 h-6 text-slate-700 mb-1 opacity-50" />
                        </div>
                    </div>
                  ))}
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
                    {currentMode === "VISHRAM" ? (
                      <>
                        <TelemetryGaugeCard label="Torso Posture" value={telemetry.torso_posture} />
                        <TelemetryGaugeCard label="Heel Alignment" value={telemetry.heel_alignment} />
                        <TelemetryGaugeCard label="Foot Angle" value={telemetry.foot_angle} />
                        <TelemetryGaugeCard label="Arm Alignment" value={telemetry.arm_alignment} />
                      </>
                    ) : (
                      <>
                        <TelemetryGaugeCard label="Torso Posture" value={telemetry.torso_posture} />
                        <TelemetryGaugeCard label="Heel Alignment" value={telemetry.heel_alignment} />
                        <TelemetryGaugeCard label="Foot Angle" value={telemetry.foot_angle} />
                        <TelemetryGaugeCard label="Arm Alignment" value={telemetry.arm_alignment} />
                      </>
                    )}
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
