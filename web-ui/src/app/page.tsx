"use client";

import React, { useEffect, useState, useRef } from "react";
import { Gauge } from "../components/Gauge";
import { Activity, Shield, Users, Camera, LayoutGrid, Settings, LogOut, ChevronRight, CheckCircle2, ChevronRightCircle, Plus, Mic, CheckCircle, XCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

type CameraMapping = {
  front: number;
  side: number;
  back: number;
};

type AppSettings = {
  confidence: number;
  pass_threshold: number;
  voice_language: string;
  show_skeleton: boolean;
  show_id_overlay: boolean;
  auto_save_session: boolean;
  image_size: number;
};

// ==========================================
// SETTINGS MODAL
// ==========================================
function SettingsModal({ isOpen, onClose, mapping, onSave, baseUrl }: {
  isOpen: boolean; onClose: () => void; mapping: CameraMapping;
  onSave: (m: CameraMapping) => void; baseUrl: string;
}) {
  const [activeTab, setActiveTab] = useState<'camera'|'system'|'display'|'session'>('camera');
  const [localMap, setLocalMap] = useState<CameraMapping>(mapping);
  const [settings, setSettings] = useState<AppSettings>({
    confidence: 0.5, pass_threshold: 85, voice_language: 'en',
    show_skeleton: true, show_id_overlay: true, auto_save_session: false, image_size: 640,
  });
  const [saveStatus, setSaveStatus] = useState<'idle'|'saving'|'saved'|'error'>('idle');

  useEffect(() => {
    if (!isOpen) return;
    setLocalMap(mapping);
    fetch(`${baseUrl}/api/settings`).then(r => r.json()).then(data => {
      setSettings(s => ({ ...s, ...data }));
    }).catch(() => {});
  }, [isOpen, mapping, baseUrl]);

  const handleSave = async () => {
    setSaveStatus('saving');
    try {
      await fetch(`${baseUrl}/api/settings`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...settings, camera_mapping: localMap }),
      });
      onSave(localMap);
      setSaveStatus('saved');
      setTimeout(() => { setSaveStatus('idle'); onClose(); }, 800);
    } catch {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 2000);
    }
  };

  if (!isOpen) return null;

  const tabs = [
    { id: 'camera' as const, label: 'Camera', icon: '📷' },
    { id: 'system' as const, label: 'System', icon: '⚙️' },
    { id: 'display' as const, label: 'Display', icon: '🖥️' },
    { id: 'session' as const, label: 'Session', icon: '📋' },
  ];

  const SliderRow = ({ label, desc, min, max, step, value, onChange }: {
    label: string; desc: string; min: number; max: number; step: number; value: number; onChange: (v: number) => void;
  }) => (
    <div className="mb-6">
      <div className="flex justify-between items-center mb-1">
        <label className="text-sm font-bold text-stone-200 uppercase tracking-widest">{label}</label>
        <span className="text-sm font-mono text-stone-300 bg-stone-800 px-2 py-0.5 rounded">{value}</span>
      </div>
      <p className="text-xs text-stone-500 mb-2">{desc}</p>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(Number(e.target.value))}
        className="w-full h-1.5 bg-stone-700 rounded-full appearance-none cursor-pointer accent-stone-300"
      />
      <div className="flex justify-between text-[10px] text-stone-600 mt-1"><span>{min}</span><span>{max}</span></div>
    </div>
  );

  const ToggleRow = ({ label, desc, value, onChange }: {
    label: string; desc: string; value: boolean; onChange: (v: boolean) => void;
  }) => (
    <div className="flex items-center justify-between mb-5 p-4 bg-stone-800/50 rounded-xl border border-white/5">
      <div>
        <div className="text-sm font-bold text-stone-200 uppercase tracking-widest">{label}</div>
        <div className="text-xs text-stone-500 mt-0.5">{desc}</div>
      </div>
      <button onClick={() => onChange(!value)}
        className={`relative w-12 h-6 rounded-full transition-colors shrink-0 ${value ? 'bg-stone-300' : 'bg-stone-700'}`}>
        <span className={`absolute top-1 w-4 h-4 rounded-full bg-stone-950 transition-all ${value ? 'left-7' : 'left-1'}`} />
      </button>
    </div>
  );

  const SelectRow = ({ label, desc, value, options, onChange }: {
    label: string; desc: string; value: string|number; options: {value: string|number; label: string}[]; onChange: (v: string) => void;
  }) => (
    <div className="mb-5">
      <label className="text-sm font-bold text-stone-200 uppercase tracking-widest">{label}</label>
      <p className="text-xs text-stone-500 mt-0.5 mb-2">{desc}</p>
      <select value={value} onChange={e => onChange(e.target.value)}
        className="w-full bg-stone-800 border border-stone-700 text-stone-200 text-sm rounded-lg px-3 py-2 outline-none focus:border-stone-500">
        {options.map(o => <option key={String(o.value)} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center">
      <div className="absolute inset-0 bg-stone-950/80 backdrop-blur-md" onClick={onClose} />
      <motion.div initial={{ opacity: 0, scale: 0.97, y: 10 }} animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        className="relative w-full max-w-2xl mx-6 bg-stone-900/98 backdrop-blur-3xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-8 py-5 border-b border-white/5">
          <div className="flex items-center gap-3">
            <img src="/top_right_logo.png" alt="SDD" className="w-10 h-10 object-contain" />
            <div>
              <h2 className="text-lg font-black text-stone-100 tracking-wide uppercase">System Settings</h2>
              <p className="text-xs text-stone-500 mt-0.5">Military Drill Analysis System · SDD, MCEME</p>
            </div>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full bg-stone-800 hover:bg-stone-700 flex items-center justify-center text-stone-400 hover:text-stone-200 transition-colors text-xl leading-none">×</button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-white/5 px-6 pt-2">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`px-4 py-2.5 text-xs font-bold uppercase tracking-widest mr-2 border-b-2 transition-colors ${activeTab === t.id ? 'text-stone-100 border-stone-300 bg-stone-800/50 rounded-t' : 'text-stone-500 border-transparent hover:text-stone-300'}`}>
              {t.icon} {t.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="px-8 py-6 max-h-[50vh] overflow-y-auto">
          {activeTab === 'camera' && (
            <div>
              <p className="text-xs text-stone-500 mb-5 uppercase tracking-widest">Map physical camera indices to their position relative to the drill subject.</p>
              {(['front', 'side', 'back'] as (keyof CameraMapping)[]).map(field => (
                <div key={field} className="flex items-center justify-between mb-4 p-4 bg-stone-800/50 rounded-xl border border-white/5">
                  <div>
                    <div className="text-sm font-bold text-stone-200 uppercase tracking-widest">{field} Camera</div>
                    <div className="text-xs text-stone-500 mt-0.5">
                      {field === 'front' ? 'Primary evaluation view' : field === 'side' ? 'Lateral posture view' : 'Rear alignment view'}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {[0, 1, 2].map(i => (
                      <button key={i} onClick={() => setLocalMap(p => ({ ...p, [field]: i }))}
                        className={`w-10 h-10 rounded-lg font-bold text-sm transition-colors ${localMap[field] === i ? 'bg-stone-300 text-stone-950' : 'bg-stone-700 text-stone-300 hover:bg-stone-600'}`}>
                        {i}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'system' && (
            <div>
              <SliderRow label="Detection Confidence" desc="Minimum YOLO pose keypoint confidence. Lower = more detections, higher = fewer false positives." min={0.1} max={0.95} step={0.05} value={settings.confidence} onChange={v => setSettings(s => ({ ...s, confidence: v }))} />
              <SliderRow label="Pass Score Threshold (%)" desc="Minimum overall score to receive a PASS verdict." min={50} max={100} step={5} value={settings.pass_threshold} onChange={v => setSettings(s => ({ ...s, pass_threshold: v }))} />
              <SelectRow label="Image Size" desc="Frame resolution for pose inference. Larger = more accurate but slower." value={settings.image_size}
                options={[{value:320,label:'320px (Fast)'},{value:480,label:'480px'},{value:640,label:'640px (Default)'},{value:1280,label:'1280px (High Accuracy)'}]}
                onChange={v => setSettings(s => ({ ...s, image_size: Number(v) }))} />
              <SelectRow label="Voice Language" desc="Language hint for the Whisper speech-to-text model." value={settings.voice_language}
                options={[{value:'en',label:'English'},{value:'hi',label:'Hindi'},{value:'auto',label:'Auto-detect'}]}
                onChange={v => setSettings(s => ({ ...s, voice_language: v }))} />
            </div>
          )}

          {activeTab === 'display' && (
            <div className="space-y-2">
              <ToggleRow label="Show ID Overlay" desc="Display detected cadet track IDs on the camera feed." value={settings.show_id_overlay} onChange={v => setSettings(s => ({ ...s, show_id_overlay: v }))} />
              <ToggleRow label="Show Skeleton Overlay" desc="Draw pose skeleton lines on the live camera feed." value={settings.show_skeleton} onChange={v => setSettings(s => ({ ...s, show_skeleton: v }))} />
            </div>
          )}

          {activeTab === 'session' && (
            <div>
              <ToggleRow label="Auto-Save Session" desc="Automatically save session results when ending a session." value={settings.auto_save_session} onChange={v => setSettings(s => ({ ...s, auto_save_session: v }))} />
              <div className="mt-4 p-5 bg-stone-800/50 rounded-xl border border-white/5">
                <div className="text-xs text-stone-500 uppercase tracking-widest mb-3">About this Build</div>
                <div className="text-stone-200 text-sm font-semibold">Military Drill Analysis System</div>
                <div className="text-stone-500 text-xs mt-1">Simulation Development Division (SDD), MCEME</div>
                <div className="mt-3 pt-3 border-t border-white/5">
                  <div className="text-stone-500 text-xs">Developed by <span className="text-stone-300 font-medium">Janardhan & Shankumar</span></div>
                  <div className="text-stone-500 text-xs mt-1">Under the guidance of <span className="text-stone-300 font-medium">Lt Col K Srinath</span></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-8 py-4 border-t border-white/5 bg-stone-950/40">
          <span className="text-xs text-stone-600">Changes are applied live to the backend</span>
          <div className="flex gap-3">
            <button onClick={onClose} className="px-5 py-2 text-sm bg-stone-800 hover:bg-stone-700 text-stone-300 rounded-lg transition-colors font-bold uppercase tracking-wider">Cancel</button>
            <button onClick={handleSave} disabled={saveStatus === 'saving'}
              className={`px-6 py-2 text-sm rounded-lg font-bold uppercase tracking-wider transition-all ${saveStatus === 'saved' ? 'bg-emerald-600 text-white' : saveStatus === 'error' ? 'bg-red-600 text-white' : 'bg-stone-200 text-stone-950 hover:bg-white'}`}>
              {saveStatus === 'saving' ? 'Saving...' : saveStatus === 'saved' ? '✓ Saved' : saveStatus === 'error' ? 'Error!' : 'Save Settings'}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

// ==========================================
// 1. LAUNCH SCREEN
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
    <>
      <div className="fixed top-8 left-8 z-[100] pointer-events-none">
        <img src="/top_right_logo.png" alt="SDD Logo" className="w-16 lg:w-20 h-auto object-contain drop-shadow-md" />
      </div>

      <motion.div
        className="fixed inset-0 z-50 flex flex-col items-center justify-center overflow-hidden font-sans"
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, scale: 1.05 }} transition={{ duration: 0.8 }}
      >
        <div className="absolute inset-0 z-0 pointer-events-none">
          <img src="/hello.jpg" alt="Background" className="w-full h-full object-cover blur-md scale-105" />
          <div className="absolute inset-0 bg-black/20"></div>
          <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
            <h1 className="text-[10rem] lg:text-[18rem] font-black font-sans tracking-tighter text-white/5 select-none whitespace-nowrap">
              INDIAN ARMY
            </h1>
          </div>
        </div>

        <div className="relative z-10 flex flex-col items-center justify-center w-full max-w-lg mt-10">
          <div className="relative w-56 h-56 mb-12 flex items-center justify-center">
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 12, repeat: Infinity, ease: "linear" }} className="absolute inset-0 border border-stone-400/10 rounded-full" />
            <motion.div animate={{ rotate: -360 }} transition={{ duration: 18, repeat: Infinity, ease: "linear" }} className="absolute inset-4 border border-stone-400/30 rounded-full border-t-transparent border-b-transparent" />
            <div className="w-40 h-40 bg-stone-800/40 backdrop-blur-2xl rounded-full shadow-2xl flex items-center justify-center border border-white/5 p-2">
              <img src="/logo.jpeg" alt="Logo" className="w-full h-full object-cover rounded-full opacity-80 mix-blend-luminosity" />
            </div>
          </div>

          <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3, duration: 0.8 }} className="text-center mb-10">
            <h1 className="text-4xl font-black tracking-[0.2em] text-stone-100 uppercase mb-2 drop-shadow-md">Drill Command</h1>
            <p className="text-xs font-bold tracking-[0.3em] text-stone-400 uppercase">Analysis System</p>
          </motion.div>

          <div className="w-64 space-y-4">
            <div className="h-[2px] w-full bg-stone-800 rounded-full overflow-hidden relative">
              <motion.div className="absolute top-0 left-0 h-full bg-stone-300" initial={{ width: 0 }} animate={{ width: `${progress}%` }} transition={{ ease: "linear", duration: 0.1 }} />
            </div>
            <div className="h-6 flex items-center justify-center overflow-hidden">
              <AnimatePresence mode="wait">
                {logs.length > 0 && (
                  <motion.div key={logs.length} initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: -10, opacity: 0 }} className="text-[10px] font-bold tracking-widest text-slate-400 uppercase text-center">
                    {logs[logs.length - 1]}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </motion.div>
    </>
  );
}

// ==========================================
// 2. ONBOARDING SCREEN
// ==========================================
function OnboardingScreen({ onNext }: { onNext: () => void }) {
  return (
    <>
      <div className="fixed top-8 left-8 z-[100] pointer-events-none">
        <img src="/top_right_logo.png" alt="SDD Logo" className="w-16 lg:w-20 h-auto object-contain drop-shadow-md" />
      </div>

      <motion.div
        className="fixed inset-0 z-40 flex items-center justify-center overflow-hidden"
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, x: -50, filter: "blur(10px)" }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <div className="absolute inset-0 z-0 pointer-events-none">
          <img src="/hello2.jpg" alt="Background" className="w-full h-full object-cover blur-md scale-105" />
          <div className="absolute inset-0 bg-black/20"></div>
          {/* Oversized Background Text */}
          <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
            <h1 className="text-[10rem] lg:text-[18rem] font-black font-sans tracking-tighter text-white/5 select-none whitespace-nowrap opacity-50">
              INDIAN ARMY
            </h1>
          </div>
        </div>

        {/* Matte Tech Grid Overlay */}
        <div className="absolute inset-0 pointer-events-none z-0">
          <div className="absolute inset-0 opacity-[0.02]"
            style={{ backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, backgroundSize: '40px 40px' }}>
          </div>
        </div>

        <div className="bg-stone-900/40 backdrop-blur-3xl shadow-2xl border border-white/5 p-12 lg:p-16 rounded-[2.5rem] max-w-7xl w-full mx-6 relative z-10 overflow-hidden">
          <img src="/hello.jpg" alt="Hero Graphic" className="absolute top-0 right-0 w-[300px] lg:w-[450px] h-auto object-contain opacity-40 rounded-bl-[100px] mix-blend-luminosity" />
          <motion.div className="relative z-10" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3, duration: 1, ease: "easeOut" }}>

            <div className="flex items-center space-x-4 mb-6">
              <img src="/logo.jpeg" alt="Logo" className="w-10 h-10 object-cover rounded-full shadow-lg border border-white/10 mix-blend-luminosity" />
              <h3 className="text-xs font-bold text-stone-400 tracking-[0.4em] uppercase opacity-90">Simulation Development Division (SDD), MCEME</h3>
            </div>

            <h1 className="text-5xl lg:text-[5.5rem] font-black text-stone-100 tracking-tighter mb-8 leading-[1.05] drop-shadow-md">
              Military Drill <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-stone-400 via-stone-300 to-stone-500">Analysis System.</span>
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

            <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mt-4">
              <div className="flex flex-col space-y-2 text-stone-400">
                <p className="text-sm tracking-wide font-medium">
                  <span className="text-stone-300 font-bold uppercase tracking-widest text-xs mr-2">Project By:</span>
                  Janardhan &amp; Shankumar
                </p>
                <p className="text-xs tracking-wider uppercase font-bold opacity-70">
                  Under the Guidance &amp; Mentorship of <span className="text-stone-300">Lt Col K Srinath</span>
                </p>
              </div>
              <button onClick={onNext} className="group shrink-0 flex items-center justify-center space-x-4 bg-stone-800 text-stone-100 border border-white/10 px-12 py-4 rounded-full font-bold text-lg hover:bg-stone-700 active:scale-95 transition-all shadow-xl">
                <span className="tracking-widest uppercase">Start</span>
                <ChevronRightCircle className="w-6 h-6 group-hover:translate-x-1 transition-transform opacity-50 group-hover:opacity-100" />
              </button>
            </div>

          </motion.div>
        </div>
      </motion.div>
    </>
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
      className="fixed inset-0 z-50 flex items-center justify-center overflow-hidden"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
    >
      <div className="absolute inset-0">
        <img src="/hello2.jpg" alt="Background" className="w-full h-full object-cover blur-md scale-105" />
        <div className="absolute inset-0 bg-stone-950/70" />
      </div>
      <div className="fixed top-8 left-8 z-[100]">
        <img src="/top_right_logo.png" alt="SDD Logo" className="w-16 h-auto object-contain drop-shadow-md" />
      </div>
      <AnimatePresence mode="wait">
        <motion.div
          key={count}
          initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 1.5, opacity: 0 }}
          transition={{ duration: 0.5 }}
          className="text-[12rem] font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-stone-100 to-stone-500 relative z-10 select-none"
        >
          {count > 0 ? count : "GO"}
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
}

// ==========================================
// TELEMETRY CARD
// ==========================================
function TelemetryGaugeCard({ label, value }: { label: string; value: any }) {
  if (typeof value === "number") return null;
  const isPass = value.status === "pass";
  return (
    <div className={`p-4 rounded-xl border backdrop-blur-sm transition-all ${isPass ? 'border-emerald-500/20 bg-emerald-950/20 hover:border-emerald-500/40' : 'border-red-500/20 bg-red-950/10 hover:border-red-500/40'}`}>
      <div className="flex justify-between items-center mb-1.5">
        <h4 className="text-[11px] font-bold text-stone-300 tracking-wider uppercase">{label}</h4>
        <div className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-widest ${isPass ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
          {isPass ? 'PASS' : 'FAIL'}
        </div>
      </div>
      <div className="text-[11px] text-stone-500 font-mono leading-relaxed">{value.reason}</div>
    </div>
  );
}

// ==========================================
// 5. MAIN DASHBOARD
// ==========================================
import { globalCadetTracker } from "@/utils/CadetTracker";

function Dashboard({ onComplete }: { onComplete: (results: any[]) => void }) {
  const BASE_URL = "http://localhost:8000";
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
  const [telemetry, setTelemetry] = useState<{ metrics: Record<string, any>; overall_score: number; status: string; detected_ids: number[]; active_mode?: string; last_command?: string; }>({
    metrics: {}, overall_score: 0, status: "Initializing...", detected_ids: [], active_mode: "SAVDHAN", last_command: ""
  });
  const [isRecording, setIsRecording] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const connectWebSocket = () => {
    const ws = new WebSocket(`ws://localhost:8000/ws/telemetry`);
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
        setTelemetry({ metrics: cleanMetrics, overall_score: overall_score || 0, status: status || "Initializing...", detected_ids: detected_ids || [], active_mode: active_mode || "SAVDHAN", last_command: last_command || "" });
      } catch (e) { console.warn("WebSocket parse error", e); }
    };
    ws.onclose = () => { setWsStatus("disconnected"); reconnectTimeout.current = setTimeout(connectWebSocket, 3000); };
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
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) mimeType = 'audio/webm;codecs=opus';
      else if (MediaRecorder.isTypeSupported('audio/mp4')) mimeType = 'audio/mp4';
      else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) mimeType = 'audio/ogg;codecs=opus';
      else if (!MediaRecorder.isTypeSupported('audio/webm')) mimeType = '';
      const options = mimeType ? { mimeType } : undefined;
      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];
      mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      mediaRecorder.onstop = async () => {
        const recordedMimeType = mediaRecorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(chunksRef.current, { type: recordedMimeType });
        const formData = new FormData();
        const extension = recordedMimeType.includes('mp4') ? '.mp4' : recordedMimeType.includes('ogg') ? '.ogg' : '.webm';
        formData.append("audio", audioBlob, `command${extension}`);
        try {
          const res = await fetch(`${BASE_URL}/api/voice_command`, { method: "POST", body: formData });
          const data = await res.json();
          if (data.error) { setVoiceError(data.error); } else { setVoiceError(null); }
        } catch (e) { setVoiceError("Network error: Could not reach backend."); }
        stream.getTracks().forEach(track => track.stop());
      };
      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) { setVoiceError("Microphone access denied or unsupported."); }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) { mediaRecorderRef.current.stop(); setIsRecording(false); }
  };

  const changeMode = (mode: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ mode }));
    }
  };

  const lockCadet = async (id: number) => {
    setSelectedCadet(id.toString());
    try {
      await fetch(`${BASE_URL}/api/lock_cadet`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ track_id: id }) });
    } catch (e) { console.error(e); }
  };

  const saveSession = () => {
    const finalScore = telemetry.overall_score;
    const isPass = finalScore >= 80;
    const newResults = [...sessionResults, { drill: telemetry.active_mode || "SAVDHAN", pass: isPass, score: finalScore }];
    setSessionResults(newResults);
    onComplete(newResults);
  };

  const isPass = telemetry.status === 'Excellent' || telemetry.status === 'Good' || telemetry.status === 'PASS';
  const isInitializing = telemetry.status === "Initializing...";

  const drillModes = [
    { label: "Savadhan", val: "SAVDHAN" },
    { label: "Vishram", val: "VISHRAM" },
    { label: "Salute", val: "FRONT_SALUTE" },
    { label: "Aaram Se", val: "AARAM_SE" }
  ];

  return (
    <motion.div className="h-screen w-full flex flex-col font-sans bg-stone-950 text-stone-100 overflow-hidden relative" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }}>
      
      {/* Settings Modal */}
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} mapping={cameraMap} onSave={persistMapping} baseUrl={BASE_URL} />

      {/* Background */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <img src="/hello2.jpg" alt="bg" className="w-full h-full object-cover blur-lg scale-110 opacity-20" />
        <div className="absolute inset-0 bg-stone-950/85" />
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, backgroundSize: '40px 40px' }} />
      </div>

      {/* Header */}
      <header className="h-16 flex items-center justify-between px-6 lg:px-8 border-b border-white/5 bg-stone-900/60 backdrop-blur-xl relative z-40 shrink-0">
        <div className="flex items-center space-x-3">
          <img src="/top_right_logo.png" alt="SDD" className="w-9 h-9 object-contain" />
          <div>
            <h1 className="text-xs font-black tracking-widest uppercase text-stone-100">Military Drill <span className="text-stone-400 font-normal">Analysis System</span></h1>
            <p className="text-[9px] text-stone-600 tracking-widest uppercase">SDD · MCEME</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {/* Mode Buttons */}
          <div className="hidden lg:flex items-center gap-1.5 bg-stone-900/80 border border-white/5 rounded-full px-2 py-1.5">
            {drillModes.map(m => (
              <button key={m.val} onClick={() => changeMode(m.val)}
                className={`px-3 py-1 text-[10px] font-bold tracking-widest uppercase rounded-full transition-all ${telemetry.active_mode === m.val ? 'bg-stone-200 text-stone-950' : 'text-stone-500 hover:text-stone-300'}`}>
                {m.label}
              </button>
            ))}
          </div>

          {/* WS Status */}
          <div className="flex items-center space-x-2 text-xs font-mono px-3 py-1.5 rounded-full border border-white/5 bg-stone-900/60">
            <span className={`w-1.5 h-1.5 rounded-full ${wsStatus === 'connected' ? 'bg-emerald-400 animate-pulse' : 'bg-red-500'}`}></span>
            <span className="text-stone-400 uppercase tracking-widest text-[9px]">{wsStatus}</span>
          </div>

          <button onClick={() => setIsSettingsOpen(true)} className="p-2 bg-stone-800/80 hover:bg-stone-700 border border-white/5 rounded-lg text-stone-400 hover:text-stone-200 transition-colors">
            <Settings className="w-4 h-4" />
          </button>
          <button onClick={saveSession} className="px-4 py-2 bg-stone-800 hover:bg-stone-700 border border-white/5 text-stone-300 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors flex items-center space-x-2">
            <LogOut className="w-3 h-3" />
            <span>End Session</span>
          </button>
        </div>
      </header>

      {/* Main Grid */}
      <main className="flex-1 p-4 lg:p-5 overflow-hidden flex flex-col lg:flex-row gap-4 relative z-10 min-h-0">

        {/* Left: Sidebar + Main View */}
        <div className="flex-1 flex gap-4 min-h-0">

          {/* Camera Sidebar */}
          <div className="w-56 flex flex-col gap-3 shrink-0">
            {(['front', 'side', 'back'] as (keyof CameraMapping)[]).map(pos => {
              const camId = cameraMap[pos];
              const isSelected = selectedCam === camId;
              return (
                <div key={pos} onClick={() => setSelectedCam(camId)}
                  className={`flex-1 relative rounded-xl overflow-hidden flex flex-col cursor-pointer border transition-all ${isSelected ? 'border-stone-400 shadow-[0_0_20px_rgba(255,255,255,0.05)]' : 'border-white/5 hover:border-stone-600'} bg-stone-900/60 backdrop-blur-sm`}>
                  <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-2.5 py-1.5 bg-stone-950/60 backdrop-blur-sm">
                    <span className="text-[9px] font-black tracking-widest text-stone-300 uppercase">{pos}</span>
                    <span className="text-[9px] font-mono text-stone-600">CAM {camId}</span>
                  </div>
                  <img
                    src={`http://localhost:8000/api/video_feed/${camId}`}
                    alt={pos}
                    className={`w-full h-full object-cover transition-opacity ${isSelected ? 'opacity-100' : 'opacity-50 group-hover:opacity-80'}`}
                    onError={(e) => { e.currentTarget.style.display = 'none'; }}
                  />
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <Activity className="w-5 h-5 text-stone-700 mb-1" />
                    <span className="text-[9px] font-bold tracking-widest uppercase text-stone-700">No Signal</span>
                  </div>
                  {isSelected && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-stone-300" />}
                </div>
              );
            })}
          </div>

          {/* Main Camera View */}
          <div className="flex-1 min-h-0 relative rounded-2xl overflow-hidden flex flex-col bg-stone-900/60 backdrop-blur-sm border border-white/5">
            {/* Top accent bar */}
            <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-stone-600 via-stone-300/60 to-transparent z-20" />

            {/* Overlays */}
            <div className="absolute top-3 left-3 z-20 flex items-center gap-2">
              <div className="px-3 py-1 bg-stone-950/70 backdrop-blur border border-white/10 rounded-full text-[10px] font-black text-stone-200 tracking-widest uppercase flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                <span>CAM {selectedCam} · {selectedCam === cameraMap.front ? 'FRONT' : selectedCam === cameraMap.side ? 'SIDE' : 'BACK'}</span>
              </div>
              {telemetry.active_mode && (
                <div className="px-3 py-1 bg-stone-950/70 backdrop-blur border border-stone-500/30 rounded-full text-[10px] font-black text-stone-300 tracking-widest uppercase">
                  {telemetry.active_mode}
                </div>
              )}
            </div>

            {/* Mobile Mode Buttons */}
            <div className="lg:hidden absolute top-3 right-3 z-20 flex gap-1.5">
              {drillModes.map(m => (
                <button key={m.val} onClick={() => changeMode(m.val)}
                  className={`px-2 py-1 text-[9px] font-bold tracking-widest uppercase rounded-full transition-all ${telemetry.active_mode === m.val ? 'bg-stone-200 text-stone-950' : 'bg-stone-900/70 border border-white/10 text-stone-400'}`}>
                  {m.label}
                </button>
              ))}
            </div>

            <div className="w-full h-full relative flex items-center justify-center">
              <img
                src={`http://localhost:8000/api/video_feed/${selectedCam}`}
                alt="Main Camera Feed"
                className="w-full h-full object-contain"
                onError={(e) => { e.currentTarget.style.display = 'none'; }}
              />
              {!selectedCadet && selectedCam === cameraMap.front && (
                <div className="absolute inset-0 z-30 flex flex-col items-center justify-center">
                  <div className="w-20 h-20 rounded-full border border-stone-600/50 flex items-center justify-center mb-5">
                    <Activity className="w-7 h-7 text-stone-500" />
                  </div>
                  <h3 className="text-base font-black text-stone-300 mb-1 tracking-widest uppercase">Awaiting Target Acquisition</h3>
                  <div className="flex gap-3 mt-4">
                    {telemetry.detected_ids && telemetry.detected_ids.length > 0 ? (
                      telemetry.detected_ids.map(id => (
                        <button key={id} onClick={() => lockCadet(id)}
                          className="px-5 py-2 bg-stone-800 border border-stone-600 text-stone-200 rounded-full font-bold text-xs tracking-widest uppercase transition-colors hover:bg-stone-700 flex items-center space-x-2">
                          <Users className="w-3.5 h-3.5" />
                          <span>Lock ID: {id}</span>
                        </button>
                      ))
                    ) : (
                      <div className="text-stone-600 font-mono text-xs uppercase tracking-widest animate-pulse">Scanning environment...</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right: Status + Telemetry */}
        <div className="lg:w-[340px] xl:w-[380px] shrink-0 flex flex-col gap-4 h-full min-h-0">

          {/* Status Panel */}
          <div className="bg-stone-900/60 backdrop-blur-sm border border-white/5 rounded-2xl p-5 flex flex-col shrink-0 relative overflow-hidden">
            <div className={`absolute top-0 left-0 w-full h-0.5 ${isInitializing ? 'bg-stone-600' : isPass ? 'bg-emerald-400' : 'bg-red-500'}`} />
            
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[10px] font-black tracking-widest text-stone-500 uppercase">Live Evaluation</h3>
              {!isInitializing && (
                <div className="text-[10px] font-mono text-stone-500">{telemetry.overall_score}% overall</div>
              )}
            </div>

            <div className="flex items-center justify-between mb-4 pb-4 border-b border-white/5">
              <div>
                <div className="text-[9px] text-stone-600 font-mono uppercase tracking-widest mb-1">Target Identity</div>
                <div className="font-black text-stone-200 text-sm">{selectedCadet ? `CADET ID-${selectedCadet}` : 'UNASSIGNED'}</div>
              </div>
              <div className="text-right">
                <div className="text-[9px] text-stone-600 font-mono uppercase tracking-widest mb-1">Mode</div>
                <div className="font-black text-stone-300 text-sm">{telemetry.active_mode || '—'}</div>
              </div>
            </div>

            <div className={`py-5 rounded-xl border flex items-center justify-center space-x-3
              ${isInitializing ? 'bg-stone-800/50 border-stone-700/50' : isPass ? 'bg-emerald-950/30 border-emerald-500/20' : 'bg-red-950/30 border-red-500/20'}`}>
              {isInitializing
                ? <Activity className="w-5 h-5 text-stone-500 animate-pulse" />
                : isPass ? <CheckCircle className="w-5 h-5 text-emerald-400" /> : <XCircle className="w-5 h-5 text-red-400" />}
              <span className={`text-2xl font-black uppercase tracking-widest ${isInitializing ? 'text-stone-500' : isPass ? 'text-emerald-400' : 'text-red-400'}`}>
                {isInitializing ? 'WAITING' : isPass ? 'PASS' : 'FAIL'}
              </span>
            </div>
          </div>

          {/* Telemetry Breakdown */}
          <div className="flex-1 min-h-0 bg-stone-900/60 backdrop-blur-sm border border-white/5 rounded-2xl p-5 flex flex-col">
            <h3 className="text-[10px] font-black tracking-widest text-stone-500 uppercase mb-4 pb-2 border-b border-white/5">Diagnostic Breakdown</h3>
            <div className="flex-1 overflow-y-auto space-y-2 pr-1">
              {Object.keys(telemetry.metrics).length === 0 ? (
                <div className="text-stone-700 text-xs italic text-center mt-10 font-mono uppercase tracking-widest animate-pulse">Waiting for target data...</div>
              ) : (
                Object.entries(telemetry.metrics).map(([label, value]) => (
                  <TelemetryGaugeCard key={label} label={label} value={value} />
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </motion.div>
  );
}

// ==========================================
// RESULTS SCREEN
// ==========================================
function ResultsScreen({ results, onRestart }: { results: any[]; onRestart: () => void }) {
  const passed = results.filter(r => r.pass).length;
  const total = results.length;

  return (
    <motion.div className="fixed inset-0 z-50 flex flex-col items-center justify-center overflow-hidden" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <div className="absolute inset-0">
        <img src="/hello2.jpg" alt="bg" className="w-full h-full object-cover blur-lg scale-110 opacity-20" />
        <div className="absolute inset-0 bg-stone-950/90" />
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, backgroundSize: '40px 40px' }} />
      </div>
      <div className="fixed top-8 left-8 z-[100]">
        <img src="/top_right_logo.png" alt="SDD Logo" className="w-16 h-auto object-contain drop-shadow-md" />
      </div>
      <div className="relative z-10 w-full max-w-3xl mx-6 p-8 bg-stone-900/80 backdrop-blur-3xl border border-white/10 rounded-3xl shadow-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-black text-stone-100 uppercase tracking-wider mb-2">Final Evaluation</h1>
          <p className="text-stone-500 text-sm">Sequence completed — strict rule-based breakdown</p>
        </div>
        <div className="grid grid-cols-3 gap-4 mb-8 text-center">
          {[
            { label: 'Total Drills', value: total, color: 'text-stone-200' },
            { label: 'Passed', value: passed, color: 'text-emerald-400' },
            { label: 'Failed', value: total - passed, color: 'text-red-400' },
          ].map(item => (
            <div key={item.label} className="p-5 bg-stone-800/50 rounded-2xl border border-white/5">
              <div className="text-xs font-black text-stone-500 tracking-widest uppercase mb-2">{item.label}</div>
              <div className={`text-4xl font-black ${item.color}`}>{item.value}</div>
            </div>
          ))}
        </div>
        <div className="space-y-2 mb-8 max-h-[40vh] overflow-y-auto pr-2">
          {results.map((r, i) => (
            <div key={i} className="flex items-center justify-between p-4 bg-stone-800/50 border border-white/5 rounded-xl">
              <div className="flex items-center space-x-4">
                <span className="text-stone-600 font-mono font-bold text-sm">{(i + 1).toString().padStart(2, '0')}</span>
                <span className="text-stone-200 font-bold">{r.drill}</span>
              </div>
              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <div className="text-[10px] text-stone-600 uppercase tracking-widest">Score</div>
                  <div className="font-mono text-stone-200 font-bold">{r.score}%</div>
                </div>
                <div className={`px-4 py-1.5 rounded-lg font-bold text-xs uppercase tracking-wider border ${r.pass ? 'bg-emerald-950/50 text-emerald-400 border-emerald-500/30' : 'bg-red-950/50 text-red-400 border-red-500/30'}`}>
                  {r.pass ? 'PASS' : 'FAIL'}
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="text-center">
          <button onClick={onRestart} className="px-10 py-4 bg-stone-200 text-stone-950 font-black uppercase tracking-widest rounded-full hover:bg-white active:scale-95 transition-all shadow-xl">
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
