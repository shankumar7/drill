"use client";

import React, { useEffect, useState, useRef } from "react";
import { Gauge } from "../components/Gauge";
import { Activity, Shield, Users, Camera, LayoutGrid, Settings, LogOut, ChevronRight, CheckCircle2, ChevronRightCircle, Plus, Mic, CheckCircle, XCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";

type CameraMapping = {
  front: number;
  side: number;
  back: number;
};

function SettingsModal({ isOpen, onClose, mapping, onSave }: { isOpen: boolean, onClose: () => void, mapping: CameraMapping, onSave: (m: CameraMapping) => void }) {
  const [localMap, setLocalMap] = useState<CameraMapping>(mapping);

  const handleChange = (field: keyof CameraMapping, value: number) => {
    setLocalMap((prev) => ({ ...prev, [field]: value }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-lg p-6 w-96">
        <h2 className="text-xl font-bold mb-4 text-slate-800">Camera Mapping</h2>
        {(['front', 'side', 'back'] as (keyof CameraMapping)[]).map((field) => (
          <div key={field} className="mb-3 flex items-center justify-between">
            <label className="text-sm font-medium text-slate-600 capitalize">{field}</label>
            <select
              className="border rounded px-2 py-1"
              value={localMap[field]}
              onChange={(e) => handleChange(field, Number(e.target.value))}
            >
              {[0, 1, 2].map((i) => (
                <option key={i} value={i}>Camera {i}</option>
              ))}
            </select>
          </div>
        ))}
        <div className="flex justify-end space-x-2 mt-4">
          <button className="px-4 py-2 text-sm bg-slate-200 hover:bg-slate-300 rounded" onClick={onClose}>Cancel</button>
          <button className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700" onClick={() => { onSave(localMap); onClose(); }}>Save</button>
        </div>
      </div>
    </div>
  );
}

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
      className="fixed inset-0 z-50 flex flex-col items-center justify-center overflow-hidden font-sans"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, scale: 1.05 }} transition={{ duration: 0.8 }}
    >
      {/* Background Image Overlay */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <img src="/hello.jpg" alt="Background" className="w-full h-full object-cover blur-md scale-105" />
        <div className="absolute inset-0 bg-black/20"></div>
        
        {/* Oversized Background Text */}
        <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
          <h1 className="text-[10rem] lg:text-[18rem] font-black font-sans tracking-tighter text-white/20 select-none whitespace-nowrap">
            INDIAN ARMY
          </h1>
        </div>
      </div>

      {/* Persistent SDD Logo */}
      <div className="absolute top-8 left-8 z-50 pointer-events-none">
        <img src="/top_right_logo.png" alt="SDD Logo" className="w-24 lg:w-32 h-auto object-contain drop-shadow-md" />
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center w-full max-w-lg mt-10">
        {/* Sleek Matte Loader */}
        <div className="relative w-56 h-56 mb-12 flex items-center justify-center">
          <motion.div 
            animate={{ rotate: 360 }} transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 border border-stone-400/10 rounded-full"
          />
          <motion.div 
            animate={{ rotate: -360 }} transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
            className="absolute inset-4 border border-stone-400/30 rounded-full border-t-transparent border-b-transparent"
          />
          <div className="w-40 h-40 bg-stone-800/40 backdrop-blur-2xl rounded-full shadow-2xl flex items-center justify-center border border-white/5 p-2">
             <img src="/logo.jpeg" alt="Logo" className="w-full h-full object-cover rounded-full opacity-80 mix-blend-luminosity" />
          </div>
        </div>

        {/* Typography */}
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3, duration: 0.8 }} className="text-center mb-10">
          <h1 className="text-4xl font-black tracking-[0.2em] text-stone-100 uppercase mb-2 drop-shadow-md">Drill Command</h1>
          <p className="text-xs font-bold tracking-[0.3em] text-stone-400 uppercase">Analysis System</p>
        </motion.div>

        {/* Minimal Progress */}
        <div className="w-64 space-y-4">
          <div className="h-[2px] w-full bg-stone-800 rounded-full overflow-hidden relative">
            <motion.div
              className="absolute top-0 left-0 h-full bg-stone-300"
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
      className="fixed inset-0 z-40 flex items-center justify-center overflow-hidden"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, x: -50, filter: "blur(10px)" }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      {/* Background Image Overlay */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <img src="/hello2.jpg" alt="Background" className="w-full h-full object-cover blur-md scale-105" />
        <div className="absolute inset-0 bg-black/20"></div>
        
        {/* Oversized Background Text */}
        <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
          <h1 className="text-[10rem] lg:text-[18rem] font-black font-sans tracking-tighter text-white/10 select-none whitespace-nowrap">
            INDIAN ARMY
          </h1>
        </div>
      </div>

      {/* Persistent SDD Logo */}
      <div className="absolute top-8 left-8 z-50 pointer-events-none">
        <img src="/top_right_logo.png" alt="SDD Logo" className="w-24 lg:w-32 h-auto object-contain drop-shadow-md" />
      </div>

      {/* Dynamic Immersive Background */}
      <div className="absolute inset-0 pointer-events-none z-0">
        {/* Matte Tech Grid Overlay */}
        <div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`,
            backgroundSize: '40px 40px'
          }}
        ></div>
      </div>

      <div className="bg-stone-900/40 backdrop-blur-3xl shadow-2xl border border-white/5 p-12 lg:p-16 rounded-[2.5rem] max-w-7xl w-full mx-6 relative z-10 overflow-hidden">
        <img 
          src="/hello.jpg" 
          alt="Hero Graphic" 
          className="absolute top-0 right-0 w-[300px] lg:w-[450px] h-auto object-contain opacity-40 rounded-bl-[100px] mix-blend-luminosity"
        />
        <motion.div className="relative z-10" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3, duration: 1, ease: "easeOut" }}>

          <div className="flex items-center space-x-4 mb-6">
            <img src="/logo.jpeg" alt="Logo" className="w-10 h-10 object-cover rounded-full shadow-lg border border-white/10 mix-blend-luminosity" />
            <h3 className="text-xs font-bold text-stone-400 tracking-[0.4em] uppercase opacity-90">
              Simulation Development Division (SDD), MCEME
            </h3>
          </div>

          <h1 className="text-5xl lg:text-[5.5rem] font-black text-stone-100 tracking-tighter mb-8 leading-[1.05] drop-shadow-md">
            Military Drill <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-stone-400 via-stone-300 to-stone-500">
              Analysis System.
            </span>
          </h1>

          <div className="flex items-center space-x-4 mb-10">
            <div className="w-32 h-[2px] bg-gradient-to-r from-stone-500 to-stone-400 rounded-full"></div>
            <div className="w-4 h-[2px] bg-stone-400 rounded-full"></div>
            <div className="w-2 h-[2px] bg-stone-400 rounded-full opacity-50"></div>
          </div>

          <p className="text-lg lg:text-xl text-stone-400 max-w-3xl leading-relaxed mb-14 font-medium">
            A professional evaluation suite designed for rigorous posture and alignment tracking.
            Initialize the workspace to begin real-time, multi-camera drill compliance assessment powered by state-of-the-art neural engines.
          </p>

          <div className="flex items-center space-x-8">
            <button
              onClick={onNext}
              className="group relative overflow-hidden flex items-center justify-center space-x-4 bg-stone-800 text-stone-100 border border-white/10 px-10 py-5 rounded-full font-bold text-lg hover:bg-stone-700 active:scale-95 transition-all shadow-xl"
            >
              <span className="relative z-10 tracking-wide uppercase">Initialize Workspace</span>
              <ChevronRightCircle className="relative z-10 w-6 h-6 group-hover:translate-x-1 transition-transform opacity-50 group-hover:opacity-100" />
            </button>
          </div>

        </motion.div>
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
function Dashboard({ onComplete }: { onComplete: (results: any[]) => void }) {
  const defaultMapping: CameraMapping = { front: 0, side: 1, back: 2 };
  const [cameraMap, setCameraMap] = useState<CameraMapping>(defaultMapping);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [selectedCam, setSelectedCam] = useState<number>(0);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("cameraMapping");
      if (saved) {
        const parsed = JSON.parse(saved);
        setCameraMap(parsed);
        setSelectedCam(parsed.front);
      }
    } catch (e) {}
  }, []);

  const persistMapping = (map: CameraMapping) => {
    localStorage.setItem("cameraMapping", JSON.stringify(map));
    setCameraMap(map);
    setSelectedCam(map.front);
  };

  const [selectedCadet, setSelectedCadet] = useState<string | null>(null);
  const [sessionResults, setSessionResults] = useState<{ drill: string, pass: boolean, score: number }[]>([]);
  const [wsStatus, setWsStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");
  
  const [telemetry, setTelemetry] = useState<{ metrics: Record<string, any>, overall_score: number, status: string, detected_ids: number[], active_mode?: string, last_command?: string }>({
    metrics: {},
    overall_score: 0,
    status: "Initializing...",
    detected_ids: [],
    active_mode: "SAVDHAN",
    last_command: ""
  });

  const [isRecording, setIsRecording] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const connectWebSocket = () => {
    const ws = new WebSocket("ws://localhost:8000/ws/telemetry");
    wsRef.current = ws;

    ws.onopen = () => setWsStatus("connected");

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const { overall_score, status, detected_ids, active_mode, last_command, ...metrics } = data;
        
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
          detected_ids: detected_ids || [],
          active_mode: active_mode || "SAVDHAN",
          last_command: last_command || ""
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
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      wsRef.current?.close();
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      let mimeType = 'audio/webm';
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus';
      } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
        mimeType = 'audio/mp4';
      } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
        mimeType = 'audio/ogg;codecs=opus';
      } else if (!MediaRecorder.isTypeSupported('audio/webm')) {
        mimeType = ''; // Let browser choose default
      }

      const options = mimeType ? { mimeType } : undefined;
      const mediaRecorder = new MediaRecorder(stream, options);
      
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const recordedMimeType = mediaRecorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(chunksRef.current, { type: recordedMimeType });
        const formData = new FormData();
        
        // Use an extension based on the mime type
        const extension = recordedMimeType.includes('mp4') ? '.mp4' : recordedMimeType.includes('ogg') ? '.ogg' : '.webm';
        formData.append("audio", audioBlob, `command${extension}`);
        
        try {
          const res = await fetch("http://localhost:8000/api/voice_command", { method: "POST", body: formData });
          const data = await res.json();
          if (data.error) {
              setVoiceError(data.error);
              console.warn("Backend Whisper Info:", data.error);
          } else {
              setVoiceError(null);
          }
        } catch (e) {
          console.error("Voice command fetch error", e);
          setVoiceError("Network error: Could not reach backend.");
        }
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Mic error", err);
      setVoiceError("Microphone access denied or unsupported.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const changeMode = (mode: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ mode }));
    }
  };

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

  const saveSession = () => {
    const finalScore = telemetry.overall_score;
    const isPass = finalScore >= 80;
    const newResults = [...sessionResults, {
      drill: telemetry.active_mode || "SAVDHAN",
      pass: isPass,
      score: finalScore
    }];
    setSessionResults(newResults);
    onComplete(newResults);
  };

  // derived status booleans
  const isPass = telemetry.status === 'Excellent' || telemetry.status === 'Good' || telemetry.status === 'PASS';
  const isInitializing = telemetry.status === "Initializing...";

  return (
    <motion.div className="h-screen w-full flex flex-col font-sans bg-slate-50 text-slate-800 overflow-hidden relative" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }}>
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} mapping={cameraMap} onSave={persistMapping} />
      
      {/* Background Tech Details */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-blue-600/10 rounded-full blur-[120px] transform translate-x-1/3 -translate-y-1/3"></div>
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-cyan-600/10 rounded-full blur-[120px] transform -translate-x-1/3 translate-y-1/3"></div>
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, backgroundSize: '40px 40px' }}></div>
      </div>

      {/* Header */}
      <header className="h-16 flex items-center justify-between px-6 lg:px-8 border-b border-slate-200 glass-header relative z-40 shrink-0">
        <div className="flex items-center space-x-4">
          <div className="w-8 h-8 rounded border border-white/20 bg-slate-800 flex items-center justify-center overflow-hidden">
             <img src="/logo.jpeg" alt="Logo" className="w-full h-full object-cover" />
          </div>
          <h1 className="text-sm font-bold tracking-widest uppercase text-slate-800">
            Military Drill <span className="text-blue-500 font-normal">Analysis System</span>
          </h1>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs font-mono">
             <span className={`w-2 h-2 rounded-full ${wsStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></span>
             <span className="text-slate-400 uppercase tracking-widest">{wsStatus}</span>
          </div>
          <button onClick={() => setIsSettingsOpen(true)} className="p-2 bg-slate-100 hover:bg-slate-200 rounded text-slate-700 transition-colors">
            <Settings className="w-4 h-4" />
          </button>
          <button onClick={saveSession} className="px-4 py-2 bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-800 rounded text-xs font-bold uppercase tracking-wider transition-colors flex items-center space-x-2">
            <LogOut className="w-3 h-3" />
            <span>End Session</span>
          </button>
        </div>
      </header>

      {/* Main Grid Content */}
      <main className="flex-1 p-4 lg:p-6 overflow-hidden flex flex-col lg:flex-row gap-6 relative z-10 w-full max-w-[2000px] mx-auto min-h-0">
        
        {/* Left Column: Camera Sidebar + Main View */}
        <div className="flex-1 flex gap-4 min-h-0">
          
          {/* Vertical Sidebar for 3 Cameras */}
          <div className="w-64 flex flex-col gap-4 shrink-0">
            {(['front', 'side', 'back'] as (keyof CameraMapping)[]).map((pos) => {
              const camId = cameraMap[pos];
              const isSelected = selectedCam === camId;
              return (
                <div 
                  key={pos} 
                  onClick={() => setSelectedCam(camId)}
                  className={`flex-1 relative glass-panel rounded-xl overflow-hidden flex items-center justify-center group cursor-pointer border-2 transition-all ${isSelected ? 'border-blue-500 shadow-md' : 'border-transparent hover:border-slate-300'}`}
                >
                  <div className="absolute top-2 left-2 z-20 px-2 py-1 bg-white/80 backdrop-blur border border-slate-200 rounded text-[9px] font-bold text-slate-700 tracking-widest uppercase shadow-sm">
                    {pos} (CAM {camId})
                  </div>
                  <img 
                    src={`http://localhost:8000/api/video_feed/${camId}`}
                    alt={pos}
                    className={`w-full h-full object-cover transition-opacity ${isSelected ? 'opacity-100' : 'opacity-60 group-hover:opacity-100'}`}
                    onError={(e) => { e.currentTarget.style.display = 'none'; }}
                  />
                  <div className="hidden absolute inset-0 flex flex-col items-center justify-center text-slate-600">
                    <Activity className="w-5 h-5 mb-1 opacity-50" />
                    <span className="text-[9px] font-bold tracking-widest uppercase">NO SIGNAL</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Main Camera View */}
          <div className="flex-1 min-h-0 relative glass-panel rounded-2xl overflow-hidden flex flex-col">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-600 via-cyan-400 to-transparent z-20"></div>
            <div className="absolute top-4 left-4 z-20 flex items-center space-x-3">
              <div className="px-3 py-1 bg-white/80 backdrop-blur border border-slate-200 rounded text-[10px] font-bold text-slate-800 tracking-widest uppercase flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                <span>CAM {selectedCam} {selectedCam === cameraMap.front ? '(FRONT)' : selectedCam === cameraMap.side ? '(SIDE)' : selectedCam === cameraMap.back ? '(BACK)' : ''}</span>
              </div>
              {telemetry.active_mode && (
                <div className="px-3 py-1 bg-blue-600/20 backdrop-blur border border-blue-500/30 rounded text-[10px] font-bold text-blue-400 tracking-widest uppercase">
                  MODE: {telemetry.active_mode}
                </div>
              )}
            </div>
            
            <div className="absolute top-4 right-4 z-20 flex gap-2">
              {[
                { label: "Savadhan", val: "SAVDHAN" },
                { label: "Vishram", val: "VISHRAM" },
                { label: "Salute", val: "FRONT_SALUTE" },
                { label: "Aaram Se", val: "AARAM_SE" }
              ].map(m => (
                <button 
                  key={m.val}
                  onClick={() => changeMode(m.val)}
                  className={`px-3 py-1.5 backdrop-blur border rounded text-[10px] font-bold tracking-widest uppercase shadow-sm transition-colors ${telemetry.active_mode === m.val ? 'bg-blue-500 text-white border-blue-600' : 'bg-white/80 border-slate-200 text-slate-700 hover:bg-slate-100'}`}
                >
                  {m.label}
                </button>
              ))}
            </div>

            <div className="w-full h-full relative flex items-center justify-center bg-slate-100/50">
              <img 
                src={`http://localhost:8000/api/video_feed/${selectedCam}`} 
                alt="Main Camera Feed" 
                className="w-full h-full object-contain"
                onError={(e) => { e.currentTarget.style.display = 'none'; }}
              />
              {(!selectedCadet && selectedCam === cameraMap.front) && (
                  <div className="absolute inset-0 z-30 flex flex-col items-center justify-center bg-white/40 backdrop-blur-[2px]">
                    <div className="w-24 h-24 border border-blue-500/50 rounded-full flex items-center justify-center relative mb-6 bg-white/80">
                       <Activity className="w-8 h-8 text-blue-500" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-800 mb-2 tracking-widest drop-shadow-md bg-white/60 px-4 py-1 rounded">AWAITING TARGET ACQUISITION</h3>
                    <div className="flex gap-3 mt-4">
                      {telemetry.detected_ids && telemetry.detected_ids.length > 0 ? (
                        telemetry.detected_ids.map(id => (
                          <button
                            key={id}
                            onClick={() => lockCadet(id)}
                            className="px-6 py-2 bg-blue-600 text-white rounded font-bold text-xs tracking-widest uppercase transition-colors shadow-lg flex items-center space-x-2"
                          >
                            <Users className="w-4 h-4" />
                            <span>LOCK ID: {id}</span>
                          </button>
                        ))
                      ) : (
                        <div className="text-slate-700 font-mono text-xs uppercase tracking-widest animate-pulse bg-white/80 px-3 py-1 rounded">Scanning environment...</div>
                      )}
                    </div>
                  </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Telemetry & Status */}
        <div className="lg:w-[400px] shrink-0 flex flex-col gap-6 h-full min-h-0">
          
          {/* Status Panel */}
          <div className="glass-panel rounded-2xl p-6 flex flex-col relative overflow-hidden shrink-0">
            <div className={`absolute top-0 left-0 w-full h-1 ${isInitializing ? 'bg-slate-500' : (isPass ? 'bg-emerald-500 shadow-[0_0_20px_#10b981]' : 'bg-red-500 shadow-[0_0_20px_#ef4444]')}`}></div>
            
            <h3 className="text-xs font-bold tracking-widest text-slate-400 uppercase mb-4">Live Evaluation Status</h3>
            
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-[10px] text-slate-500 font-mono uppercase tracking-widest mb-1">Target Identity</div>
                <div className="font-bold text-slate-800">{selectedCadet ? `CADET ID-${selectedCadet}` : 'UNASSIGNED'}</div>
              </div>
              <div className="text-right">
                <div className="text-[10px] text-slate-500 font-mono uppercase tracking-widest mb-1">System Confidence</div>
                <div className="font-bold text-blue-400">92%</div>
              </div>
            </div>

            <div className={`mt-2 py-4 rounded-xl border flex items-center justify-center space-x-3
              ${isInitializing ? 'bg-slate-800/50 border-slate-700/50 text-slate-400' : 
                (isPass ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400')}`}>
              {isInitializing ? <Activity className="w-6 h-6 animate-pulse" /> : (isPass ? <CheckCircle className="w-6 h-6" /> : <XCircle className="w-6 h-6" />)}
              <span className="text-3xl font-black uppercase tracking-widest drop-shadow-md">
                {isInitializing ? "WAITING" : (isPass ? "PASS" : "FAIL")}
              </span>
            </div>
            
            {!isInitializing && (
              <div className="mt-4 text-center">
                 <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">Overall Score</div>
                 <div className="text-2xl font-bold text-slate-800">{telemetry.overall_score}%</div>
              </div>
            )}
          </div>

          {/* Telemetry Metrics List */}
          <div className="flex-1 min-h-0 glass-panel rounded-2xl p-5 flex flex-col relative">
            <h3 className="text-xs font-bold tracking-widest text-slate-400 uppercase mb-4 pb-2 border-b border-white/5">Diagnostic Breakdown</h3>
            
            <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-3">
              {Object.keys(telemetry.metrics).length === 0 ? (
                <div className="text-slate-600 text-xs italic text-center mt-10 font-mono uppercase tracking-widest">Waiting for target data...</div>
              ) : (
                Object.entries(telemetry.metrics).map(([label, value]) => (
                  <TelemetryGaugeCard key={label} label={label} value={value} />
                ))
              )}
            </div>
          </div>

        </div>
      </main>

      {/* Floating Voice Command Bar (Temporarily Disabled) */}
      {/*
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 flex flex-col items-center">
        {voiceError && (
           <div className="mb-3 px-4 py-2 bg-red-50/90 backdrop-blur-md rounded-lg border border-red-200 text-xs font-mono text-red-600 shadow-lg text-center max-w-sm">
             <span className="font-bold">Error:</span> {voiceError.includes('ffmpeg') ? "FFmpeg is missing on the backend. Please install it." : voiceError}
           </div>
        )}
        {telemetry.last_command && !voiceError && (
           <div className="mb-3 px-4 py-1.5 bg-white/90 backdrop-blur-md rounded-full border border-slate-200 text-xs font-mono text-slate-700">
             Heard: <span className="text-blue-400 font-bold uppercase">"{telemetry.last_command}"</span>
           </div>
        )}
        <div className="flex items-center p-2 bg-white/90 backdrop-blur-xl border border-slate-200 rounded-full shadow-[0_10px_40px_rgba(0,0,0,0.1)]">
          <button 
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onMouseLeave={stopRecording}
            onTouchStart={startRecording}
            onTouchEnd={stopRecording}
            className={`flex items-center space-x-3 px-8 py-4 rounded-full font-bold uppercase tracking-widest text-sm transition-all relative overflow-hidden
              ${isRecording 
                ? 'bg-blue-600 text-white shadow-[0_0_30px_rgba(37,99,235,0.5)] scale-105' 
                : 'bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white'}`}
          >
            {isRecording && <div className="absolute inset-0 bg-blue-400/20 animate-ping rounded-full"></div>}
            <Mic className={`w-5 h-5 relative z-10 ${isRecording ? 'text-white animate-pulse' : 'text-blue-500'}`} />
            <span className="relative z-10">{isRecording ? "Listening..." : "Hold to Speak"}</span>
          </button>
        </div>
      </div>
      */}

    </motion.div>
  );
}


function TelemetryGaugeCard({ label, value }: { label: string; value: any }) {
  if (typeof value === "number") return null; 
  const isPass = value.status === "pass";
  return (
    <div className={`p-3 rounded-lg border bg-white/80 shadow-sm backdrop-blur-sm transition-colors
      ${isPass ? 'border-emerald-500/20 hover:border-emerald-500/40' : 'border-red-500/20 hover:border-red-500/40'}`}>
      <div className="flex justify-between items-center mb-1.5">
        <h4 className="text-[11px] font-bold text-slate-700 tracking-wider uppercase">{label}</h4>
        <div className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-widest ${isPass ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
          {isPass ? 'PASS' : 'FAIL'}
        </div>
      </div>
      <div className="text-[11px] text-slate-500 font-mono leading-relaxed">
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
          <div className="p-6 bg-white shadow-sm rounded-2xl border border-slate-200">
            <div className="text-sm font-bold text-slate-500 tracking-widest uppercase mb-2">Total Drills</div>
            <div className="text-4xl font-black text-slate-900">{total}</div>
          </div>
          <div className="p-6 bg-white shadow-sm rounded-2xl border border-slate-200">
            <div className="text-sm font-bold text-slate-500 tracking-widest uppercase mb-2">Passed</div>
            <div className="text-4xl font-black text-emerald-400">{passed}</div>
          </div>
          <div className="p-6 bg-white shadow-sm rounded-2xl border border-slate-200">
            <div className="text-sm font-bold text-slate-500 tracking-widest uppercase mb-2">Failed</div>
            <div className="text-4xl font-black text-red-400">{total - passed}</div>
          </div>
        </div>
        <div className="space-y-3 mb-10 max-h-[40vh] overflow-y-auto custom-scrollbar pr-4">
          {results.map((r, i) => (
            <div key={i} className="flex items-center justify-between p-4 bg-white shadow-sm border border-slate-200 rounded-xl">
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
  const [appState, setAppState] = useState<"launch" | "onboarding" | "countdown" | "dashboard" | "results">("launch");
  const [finalResults, setFinalResults] = useState<any[]>([]);

  return (
    <AnimatePresence mode="wait">
      {appState === "launch" && (
        <LaunchScreen key="launch" onComplete={() => setAppState("onboarding")} />
      )}
      {appState === "onboarding" && (
        <OnboardingScreen key="onboard" onNext={() => setAppState("dashboard")} />
      )}
      {appState === "dashboard" && (
        <Dashboard key="dashboard" onComplete={(results) => { setFinalResults(results); setAppState("results"); }} />
      )}
      {appState === "results" && (
        <ResultsScreen key="results" results={finalResults} onRestart={() => setAppState("launch")} />
      )}
    </AnimatePresence>
  );
}
